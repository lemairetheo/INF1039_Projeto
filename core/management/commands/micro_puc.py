import time
from io import StringIO
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

# Importações específicas para compatibilidade com o macOS e servidores
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# Importações oficiais do Django
from django.core.management.base import BaseCommand
from core.models import Disciplina, Professor, Turma, DiaSemanaAula  # Importado DiaSemanaAula


class Command(BaseCommand):
    help = "Dispara o Web Scraper da PUC, varre todas as páginas e alimenta o banco relacional do Django"

    def handle(self, *args, **options):
        # ==============================================================================
        # PASSO 1: CONFIGURAR E ABRIR O SITE NO NAVEGADOR (HEADLESS)
        # ==============================================================================
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")  # Executa em segundo plano (sem abrir janela)
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        self.stdout.write(self.style.WARNING("Configurando driver do Chrome..."))
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        self.stdout.write(self.style.WARNING("Acessando a página do Microhorário da PUC..."))
        url = "https://microhorario.rdc.puc-rio.br/WebMicroHorarioConsulta/MicroHorarioConsulta.aspx?sessao=U2lzdGVtYT1QVUNPTkxJTkVfQUxVTk8mQXBsaWNhY2FvPU1JQ1JPX0hPUkFSSU8mRnVuY2FvPUhPUkFSSU9fU0FMQSZJRD1iODk0ZjU2MmU5MjQ0ZTViYjk3Mzk2ZmFjNDg3ZDY4Yw__"

        driver.get(url)
        time.sleep(3)

        try:
            self.stdout.write("Tentando clicar no botão 'Buscar' para listar todas as disciplinas...")
            try:
                botao_buscar = driver.find_element(By.XPATH, "//a[contains(text(), 'Buscar') or contains(text(), 'Consultar')]")
            except:
                botao_buscar = driver.find_element(By.XPATH, "//input[@type='submit' or @value='Buscar']")
                
            botao_buscar.click()
            self.stdout.write(self.style.SUCCESS("Botão clicado com sucesso! Iniciando a paginação..."))
            time.sleep(4)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"[Erro Inicial] Não foi possível iniciar a busca no site: {e}"))
            driver.quit()
            return

        todos_os_dfs = []
        pagina_atual = 1

        # ==============================================================================
        # PASSO 2: LOOP PARA COLETAR OS DADOS PÁGINA POR PÁGINA (ATÉ O FIM DO SITE)
        # ==============================================================================
        while True:
            self.stdout.write(f"Lendo e processando dados da página {pagina_atual} ...")
            
            html_content = driver.page_source
            soup = BeautifulSoup(html_content, 'html.parser')
            tabelas_html = soup.find_all('table')
            
            tabela_encontrada = False
            for tab in tabelas_html:
                df_lista = pd.read_html(StringIO(str(tab)))
                
                if df_lista and len(df_lista[0].columns) >= 10:
                    df_pagina = df_lista[0].iloc[:, :10]
                    df_pagina.columns = ["Disciplina", "codigo", "nome", "professor", "credito", "", "", "", "", "horario_sala"]
                    todos_os_dfs.append(df_pagina)
                    tabela_encontrada = True
                    break
                    
            if not tabela_encontrada:
                self.stdout.write(self.style.WARNING(f"Aviso: Nenhuma tabela detectada na página {pagina_atual}."))

            # --- LÓGICA DE NAVEGAÇÃO ENTRE PÁGINAS ---
            proxima_pagina = pagina_atual + 1
            try:
                link_proxima = driver.find_element(By.XPATH, f"//a[text()='{proxima_pagina}']")
                driver.execute_script("arguments[0].scrollIntoView();", link_proxima)
                time.sleep(0.5)
                link_proxima.click()
                pagina_atual = proxima_pagina
                time.sleep(4)
            except:
                try:
                    link_reticencias = driver.find_element(By.XPATH, f"//a[contains(@href, \"Page${proxima_pagina}\")]")
                    driver.execute_script("arguments[0].scrollIntoView();", link_reticencias)
                    link_reticencias.click()
                    pagina_atual += 1
                    time.sleep(4)
                except:
                    self.stdout.write(self.style.SUCCESS("\nChegamos ao fim definitivo de todas as páginas do site!"))
                    break

        driver.quit()

        # ==============================================================================
        # PASSO 3: TRATAMENTO DOS DADOS E SALVAMENTO RELACIONAL NO DJANGO
        # ==============================================================================
        if todos_os_dfs:
            self.stdout.write(self.style.WARNING("\nIniciando a limpeza e mapeamento dos dados..."))
            
            df_final = pd.concat(todos_os_dfs, ignore_index=True)
            df_final["Disciplina"] = df_final["Disciplina"].astype(str)
            df_final["codigo"] = df_final["codigo"].astype(str)
            
            # Filtros de Higienização do DataFrame
            df_final = df_final[df_final["Disciplina"].str.contains("Disciplina", na=False) == False]
            palavras_para_remover = ["Último", "Primeiro", "<<", ">>", "antigos"]
            for palavra in palavras_para_remover:
                df_final = df_final[df_final["Disciplina"].str.contains(palavra, na=False, case=False) == False]
                df_final = df_final[df_final["codigo"].str.contains(palavra, na=False, case=False) == False]
            
            df_final = df_final[df_final["codigo"].str.strip().str.len() > 3]
            df_final["nome"] = df_final["nome"].astype(str).str.strip()
            df_final["codigo"] = df_final["codigo"].astype(str).str.strip()
            
            df_final.fillna("", inplace=True)
            df_final = df_final[df_final["nome"] != ""]
            df_final = df_final[df_final["codigo"] != ""]
            df_final = df_final.loc[:, df_final.columns != ""]
            
            self.stdout.write(self.style.WARNING("Salvando dados no Banco Relacional do Django..."))
            registros_salvos = 0
            registros_com_erro = 0
            
            for index, row in df_final.iterrows():
                try:
                    v_codigo = str(row['codigo']).strip()
                    v_nome = str(row['nome']).strip()
                    v_nome_professor = str(row['professor']).strip() if row['professor'] != "" else "Não Informado"

                    # 1. Tratamento Avançado do Horário da PUC (Ex: "2A 07:00-09:00", "4C 11:00-13:00")
                    v_horario_cru = str(row['horario_sala']).strip().upper()
                    
                    # Mapeamento do padrão numérico da PUC para a sua classe DiaSemana
                    mapa_dias = {
                        "2": "SEG",
                        "3": "TER",
                        "4": "QUA",
                        "5": "QUI",
                        "6": "SEX",
                        "7": "SAB"
                    }
                    
                    # Descobre os dias da semana presentes no texto
                    codigos_dias_encontrados = []
                    for digito, sigla in mapa_dias.items():
                        if digito in v_horario_cru:
                            codigos_dias_encontrados.append(sigla)

                    # --- NOVA LÓGICA DE CRÉDITOS ---
                    # Conta a quantidade de dias encontrados. Se não achar nenhum no texto, assume o mínimo de 1 dia.
                    total_dias = len(codigos_dias_encontrados) if len(codigos_dias_encontrados) > 0 else 1
                    creditos_calculados = total_dias * 2

                    # 2. Salva/Atualiza a Disciplina mapeada utilizando os créditos calculados
                    disciplina_obj, _ = Disciplina.objects.update_or_create(
                        codigo=v_codigo,
                        defaults={
                            'nome': v_nome,
                            'creditos': creditos_calculados,  # Substituído pelo cálculo: (Dias da semana * 2)
                            'periodo': 1,  
                        }
                    )

                    # 3. Salva/Atualiza o Professor responsável
                    professor_obj, _ = Professor.objects.get_or_create(
                        nome=v_nome_professor,
                        defaults={
                            'departamento': 'Geral'
                        }
                    )

                    # Mapeamento do intervalo de horas da PUC para o Choice do seu Model
                    horario_selecionado = "07-09"  # Padrão caso falhe o parse
                    mapa_horarios = {
                        "07:00": "07-09",
                        "09:00": "09-11",
                        "11:00": "11-13",
                        "13:00": "13-15",
                        "15:00": "15-17",
                        "17:00": "17-19",
                        "19:00": "19-21",
                    }
                    
                    for hora_inicio, choice_valor in mapa_horarios.items():
                        if hora_inicio in v_horario_cru:
                            horario_selecionado = choice_valor
                            break

                    # 4. Cria ou atualiza a Turma vinculando as chaves estrangeiras corretas
                    turma_obj, _ = Turma.objects.get_or_create(
                        disciplina=disciplina_obj,
                        professor=professor_obj,
                        horario=horario_selecionado
                    )

                    # 5. Vincula os dias da semana coletados (Lógica ManyToMany)
                    if codigos_dias_encontrados:
                        dias_projeto = []
                        for cod_dia in codigos_dias_encontrados:
                            dia_aula_obj, _ = DiaSemanaAula.objects.get_or_create(dia=cod_dia)
                            dias_projeto.append(dia_aula_obj)
                        
                        # Associa os dias capturados à turma
                        turma_obj.dias_semana.set(dias_projeto)
                    else:
                        # Fallback seguro caso não ache nenhum dia estruturado no texto
                        dia_padrao, _ = DiaSemanaAula.objects.get_or_create(dia="SEG")
                        turma_obj.dias_semana.set([dia_padrao])

                    registros_salvos += 1

                except Exception as erro_linha:
                    registros_com_erro += 1
                    self.stdout.write(self.style.ERROR(
                        f"Erro ao salvar linha {index} (Código: {row.get('codigo', 'Desconhecido')}): {erro_linha}"
                    ))
                    continue

            # Relatório final impresso no terminal
            self.stdout.write(self.style.SUCCESS(
                f"\n=========================================================="
                f"\nPROCESSO CONCLUÍDO COM SUCESSO!"
                f"\n- Total de páginas coletadas: {pagina_atual}"
                f"\n- {registros_salvos} registros inseridos com sucesso (Mapeamento Relacional)."
                f"\n- {registros_com_erro} linhas ignoradas por erros críticos."
                f"\n=========================================================="
            ))
        else:
            self.stdout.write(self.style.ERROR("\nNenhum dado pôde ser extraído do site."))
