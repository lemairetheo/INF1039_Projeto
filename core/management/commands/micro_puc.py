import time
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Importações específicas para compatibilidade com o macOS e servidores
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# Importações oficiais baseadas estritamente nas suas novas Models
from django.core.management.base import BaseCommand
from core.models import Disciplina, Professor, Turma, DiaSemanaAula, DiaSemana, Horario, Status


class Command(BaseCommand):
    help = "Dispara o Web Scraper da PUC, varre o SITE COMPLETO e alimenta o banco relacional do Django"

    def handle(self, *args, **options):
        # ------------------------------------------------------------------------------
        # PASSO ZERO: LIMPEZA PREVENTIVA DO BANCO DE DADOS
        # ------------------------------------------------------------------------------
        self.stdout.write(self.style.WARNING("Limpando turmas antigas para evitar conflitos..."))
        Turma.objects.all().delete()

        # ==============================================================================
        # PASSO 1: CONFIGURAR E ABRIR O SITE NO NAVEGADOR
        # ==============================================================================
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
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
                botao_buscar = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Buscar') or contains(text(), 'Consultar')]"))
                )
            except:
                botao_buscar = driver.find_element(By.XPATH, "//input[@type='submit' or @value='Buscar']")
                
            botao_buscar.click()
            self.stdout.write(self.style.SUCCESS("Botão 'Buscar' clicado com sucesso! Iniciando extração total..."))
            time.sleep(5)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"[Erro Inicial] Falha ao iniciar busca: {e}"))
            driver.quit()
            return

        linhas_coletadas_brutas = []
        pagina_atual = 1

        # ==============================================================================
        # PASSO 2: EXTRAÇÃO INFINITA ATÉ O FIM DAS PÁGINAS DO SITE
        # ==============================================================================
        while True:
            self.stdout.write(f"Processando HTML da página {pagina_atual} ...")
            
            try:
                # Aguarda o GridView carregar
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "zw-rgrid"))
                )
                
                html_content = driver.page_source
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Encontra todas as linhas de dados (tab_linha1 e tab_linha2)
                linhas_tr = soup.find_all('tr', class_=re.compile(r'tab_linha'))
                
                pag_linhas_contadas = 0
                for tr in linhas_tr:
                    dados_linha = {}
                    tds = tr.find_all('td')
                    for td in tds:
                        th_nome = td.get('data-th')
                        if th_nome:
                            texto_limpo = td.get_text(separator=" ").replace('"', '').strip()
                            dados_linha[th_nome] = texto_limpo
                    
                    if "Disciplina" in dados_linha and "Nome da disciplina" in dados_linha:
                        linhas_coletadas_brutas.append(dados_linha)
                        pag_linhas_contadas += 1
                
                self.stdout.write(self.style.SUCCESS(f"   -> [OK] Coletadas {pag_linhas_contadas} matérias na página {pagina_atual}. Total acumulado: {len(linhas_coletadas_brutas)}"))
                
                proxima_pagina = pagina_atual + 1
                avançou = False

                # 1ª Tentativa: Clicar no link direto do número (Ex: se está na 3, clica na '4')
                try:
                    link_proxima = driver.find_element(By.XPATH, f"//a[text()='{proxima_pagina}']")
                    driver.execute_script("arguments[0].scrollIntoView();", link_proxima)
                    time.sleep(0.3)
                    link_proxima.click()
                    pagina_atual = proxima_pagina
                    avançou = True
                    time.sleep(4)  # Tempo para o PostBack carregar os dados
                except:
                    pass

                # 2ª Tentativa: Se não achou o número direto, pode ser a mudança de bloco (ex: da página 10 para 11 usando o link '...')
                if not avançou:
                    try:
                        # Procura o link de reticências que aponte explicitamente para o script da página alvo
                        link_reticencias = driver.find_element(By.XPATH, f"//a[contains(@href, 'Page${proxima_pagina}')]")
                        driver.execute_script("arguments[0].scrollIntoView();", link_reticencias)
                        time.sleep(0.3)
                        link_reticencias.click()
                        pagina_atual = proxima_pagina
                        avançou = True
                        time.sleep(5)
                    except:
                        pass

                # Se nenhuma das opções funcionou, significa que realmente chegamos na última página disponível do site
                if not avançou:
                    self.stdout.write(self.style.SUCCESS(f"\n[FIM] Fim das páginas alcançado na página {pagina_atual}! Iniciando gravação dos dados..."))
                    break

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erro ao processar página {pagina_atual}: {e}. Interrompendo coleta preventiva para salvar o que já foi pego."))
                break

        driver.quit()

        # ==============================================================================
        # PASSO 3: MAPEAMENTO E GRAVAÇÃO RELACIONAL NO BANCO DJANGO
        # ==============================================================================
        if linhas_coletadas_brutas:
            self.stdout.write(self.style.WARNING(f"\nAlimentando o banco de dados com {len(linhas_coletadas_brutas)} registros..."))
            
            # Garante os Enums
            dias_db_mapeados = {}
            for escolha in DiaSemana.choices:
                sigla = escolha[0]
                dia_obj, _ = DiaSemanaAula.objects.get_or_create(dia=sigla)
                dias_db_mapeados[sigla] = dia_obj

            mapa_horarios_puc = {
                7: Horario.H07_09.value,
                9: Horario.H09_11.value,
                11: Horario.H11_13.value,
                13: Horario.H13_15.value,
                15: Horario.H15_17.value,
                17: Horario.H17_19.value,
                19: Horario.H19_21.value,
            }
            
            registros_salvos = 0
            registros_com_erro = 0
            
            for item in linhas_coletadas_brutas:
                try:
                    v_codigo = item.get("Disciplina", "").strip()
                    v_nome = item.get("Nome da disciplina", "").strip()
                    v_professor = item.get("Professor", "Não Informado").strip()
                    v_horario_cru = item.get("Horário/Sala", "").upper().strip()
                    
                    if not v_codigo or len(v_codigo) < 4:
                        continue
                        
                    if not v_horario_cru:
                        continue

                    # Regex focado nas strings limpas que vimos no DOM
                    padrao_horario = re.compile(r'([A-Z]{3})\s+(\d{1,2}-\d{1,2})')
                    matches = padrao_horario.findall(v_horario_cru)

                    if not matches:
                        continue

                    dias_da_linha = set()
                    horarios_da_linha = set()
                    dias_instancias = []

                    for sigla_dia, bloco_horas in matches:
                        if sigla_dia in dias_db_mapeados:
                            dias_da_linha.add(sigla_dia)
                            if dias_db_mapeados[sigla_dia] not in dias_instancias:
                                dias_instancias.append(dias_db_mapeados[sigla_dia])

                            try:
                                h_inicio, h_fim = map(int, bloco_horas.split('-'))
                                for hora_atual in range(h_inicio, h_fim, 2):
                                    if hora_atual in mapa_horarios_puc:
                                        horarios_da_linha.add(mapa_horarios_puc[hora_atual])
                            except ValueError:
                                pass

                    if not dias_instancias or not horarios_da_linha:
                        continue

                    creditos_calculados = len(dias_da_linha) * 2

                    # 1. Salva/Atualiza a Disciplina
                    disciplina_obj, _ = Disciplina.objects.update_or_create(
                        codigo=v_codigo,
                        defaults={
                            'nome': v_nome,
                            'creditos': creditos_calculados,
                            'periodo': 1,
                            'status': Status.SOB_AVALIACAO.value
                        }
                    )

                    # 2. Salva o Professor
                    professor_obj, _ = Professor.objects.get_or_create(
                        nome=v_professor if v_professor != "" else "Não Informado",
                        defaults={'departamento': 'Geral'}
                    )

                    # 3. Cria as turmas mapeando os Horários separados
                    for hor_selecionado in horarios_da_linha:
                        turma_obj, _ = Turma.objects.get_or_create(
                            disciplina=disciplina_obj,
                            professor=professor_obj,
                            horario=hor_selecionado
                        )
                        turma_obj.dias_semana.set(dias_instancias)

                    registros_salvos += 1

                except Exception:
                    registros_com_erro += 1
                    continue

            self.stdout.write(self.style.SUCCESS(
                f"\n=========================================================="
                f"\nPROCESSO DE RASPAGEM TOTAL CONCLUÍDO!"
                f"\n- Total de páginas processadas: {pagina_atual}"
                f"\n- {registros_salvos} turmas/matérias inseridas com sucesso."
                f"\n- {registros_com_erro} erros de processamento ignorados."
                f"\n=========================================================="
            ))
        else:
            self.stdout.write(self.style.ERROR("\nNenhum dado pôde ser extraído do site."))
