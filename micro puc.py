import re
import time
import traceback
from io import StringIO

import pandas as pd
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.models import Disciplina, Professor, Turma

DIAS_MAP = {
    "2": "SEG",
    "3": "TER",
    "4": "QUA",
    "5": "QUI",
    "6": "SEX",
    "7": "SAB",
}


def extrair_dias_horarios(texto):
    texto = str(texto or "").upper()
    resultados = []
    padrao = r"([234567]+)([A-Z]+)"

    for dias, horarios in re.findall(padrao, texto):
        for d in dias:
            dia = DIAS_MAP.get(d)
            if dia:
                resultados.append((dia, horarios))

    return resultados


class Command(BaseCommand):
    help = "Importa dados do MicroHorário da PUC para o banco do Django e gera CSV"

    def criar_driver(self):
        options = webdriver.ChromeOptions()
        # Se quiser rodar sem abrir a janela do navegador, descomente a linha abaixo:
        # options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        return webdriver.Chrome(options=options)

    def salvar_debug(self, driver):
        try:
            driver.save_screenshot("erro_microhorario.png")
            with open("microhorario_debug.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
        except Exception:
            pass

    def handle(self, *args, **options):
        driver = self.criar_driver()

        try:
            # URL atualizada enviada pelo usuário (Horário/Sala)
            url = (
                "https://microhorario.rdc.puc-rio.br/"
                "WebMicroHorarioConsulta/"
                "MicroHorarioConsulta.aspx?sessao="
                "U2lzdGVtYT1QVUNPTkxJTkVfQUxVTk8m"
                "QXBsaWNhY2FvPU1JQ1JPX0hPUkFSSU8m"
                "RnVuY2FvPUhPUkFSSU9fU0FMQSZJRD04"
                "OTJjOWY4NjAxZjM0NzdhODBlNjQxMTdl"
                "YWViM2U1ZQ__"
            )

            self.stdout.write("Acessando a página do Microhorário da PUC (Nova URL)...")
            driver.get(url)
            time.sleep(3)

            # ==================================================================
            # PASSO 1: CLICAR NO BOTÃO BUSCAR / CONSULTAR
            # ==================================================================
            self.stdout.write("Tentando clicar no botão para listar todas as disciplinas...")
            try:
                try:
                    botao_buscar = driver.find_element(
                        By.XPATH, "//a[contains(text(), 'Buscar') or contains(text(), 'Consultar')]"
                    )
                except Exception:
                    botao_buscar = driver.find_element(
                        By.XPATH, "//input[@type='submit' or @value='Buscar' or @id='btnConsultar']"
                    )

                botao_buscar.click()
                self.stdout.write(self.style.SUCCESS("Botão clicado com sucesso! Iniciando varredura..."))
                time.sleep(4)

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"[Erro Inicial] Não foi possível iniciar a busca: {e}"))
                self.salvar_debug(driver)
                driver.quit()
                return

            # ==================================================================
            # PASSO 2: LOOP DE PAGINAÇÃO E COLETA
            # ==================================================================
            todos_os_dfs = []
            pagina_atual = 1

            while True:
                self.stdout.write(f"Lendo e processando os dados da página {pagina_atual} ...")
                
                html_content = driver.page_source
                soup = BeautifulSoup(html_content, 'html.parser')
                tabelas_html = soup.find_all('table')
                
                tabela_encontrada = False
                for tab in tabelas_html:
                    try:
                        df_lista = pd.read_html(StringIO(str(tab)))
                        
                        if df_lista and len(df_lista[0].columns) >= 10:
                            df_pagina = df_lista[0].iloc[:, :10].copy()
                            
                            df_pagina.columns = [
                                "codigo_turma",  
                                "codigo",
                                "nome",
                                "professor",
                                "credito",
                                "vagas",
                                "inscritos",
                                "status",
                                "horario_sala",
                                "extra",
                            ]
                            
                            todos_os_dfs.append(df_pagina)
                            tabela_encontrada = True
                            break
                    except Exception:
                        continue
                        
                if not tabela_encontrada:
                    self.stdout.write(
                        self.style.WARNING(f"Aviso: Nenhuma tabela detectada na página {pagina_atual}.")
                    )

                # --- LÓGICA DE NAVEGAÇÃO AVANÇADA (TRATA RETICÊNCIAS) ---
                proxima_pagina = pagina_atual + 1
                try:
                    link_proxima = driver.find_element(By.XPATH, f"//a[text()='{proxima_pagina}']")
                    driver.execute_script("arguments[0].scrollIntoView();", link_proxima)
                    time.sleep(0.5)
                    link_proxima.click()
                    
                    pagina_atual = proxima_pagina
                    time.sleep(4)
                    
                except Exception:
                    try:
                        link_reticencias = driver.find_element(
                            By.XPATH, f"//a[contains(@href, \"Page${proxima_pagina}\")]"
                        )
                        driver.execute_script("arguments[0].scrollIntoView();", link_reticencias)
                        link_reticencias.click()
                        
                        pagina_atual = proxima_pagina
                        time.sleep(4)
                    except Exception:
                        self.stdout.write(self.style.SUCCESS("\nChegamos ao fim de todas as páginas disponíveis!"))
                        break

            driver.quit()

            # ==================================================================
            # PASSO 3: TRATAMENTO E LIMPEZA DOS DADOS (PANDAS)
            # ==================================================================
            if not todos_os_dfs:
                self.stdout.write(self.style.ERROR("\nNenhum dado pôde ser extraído do site."))
                return

            self.stdout.write("\nIniciando o processo de limpeza dos dados coletados...")
            df_final = pd.concat(todos_os_dfs, ignore_index=True)
            
            df_final["codigo_turma"] = df_final["codigo_turma"].astype(str)
            df_final["codigo"] = df_final["codigo"].astype(str)
            
            df_final = df_final[~df_final["codigo_turma"].str.contains("Disciplina", na=False, case=False)]
            
            palavras_para_remover = ["Último", "Primeiro", "<<", ">>", "antigos"]
            for palavra in palavras_para_remover:
                df_final = df_final[~df_final["codigo_turma"].str.contains(palavra, na=False, case=False)]
                df_final = df_final[~df_final["codigo"].str.contains(palavra, na=False, case=False)]
            
            df_final = df_final[df_final["codigo"].str.strip().str.len() > 3]
            
            df_final["nome"] = df_final["nome"].astype(str).str.strip()
            df_final["codigo_turma"] = df_final["codigo_turma"].astype(str).str.strip()
            df_final["codigo"] = df_final["codigo"].astype(str).str.strip()
            
            df_final.replace("", pd.NA, inplace=True)
            df_final = df_final.dropna(subset=["nome", "codigo"])
            df_final = df_final.loc[:, df_final.columns != ""]

            # Exportação do CSV local para conferência rápida
            df_final.to_csv("microhorario_puc_completo.csv", index=False, encoding="utf-8-sig")
            self.stdout.write("Backup de segurança salvo em 'microhorario_puc_completo.csv'.")

            # ==================================================================
            # PASSO 4: SALVAR DADOS NO DJANGO ORM
            # ==================================================================
            disciplinas_criadas = 0
            professores_criados = 0
            turmas_criadas = 0

            self.stdout.write("Inserindo/Atualizando os registros no banco de dados...")

            for _, row in df_final.iterrows():
                professor_nome = str(row.get("professor", "")).strip()
                if not professor_nome or professor_nome == "<NA>":
                    professor_nome = "Não informado"

                professor, criado = Professor.objects.get_or_create(
                    nome=professor_nome,
                    defaults={"departamento": "Não informado"},
                )
                if criado:
                    professores_criados += 1

                try:
                    creditos = int(float(row.get("credito", 0)))
                except Exception:
                    creditos = 0

                disciplina, criada = Disciplina.objects.update_or_create(
                    codigo=row["codigo_turma"],
                    defaults={
                        "nome": row["nome"],
                        "creditos": creditos,
                        "periodo": 0,
                    },
                )
                if criada:
                    disciplinas_criadas += 1

                horarios = extrair_dias_horarios(row.get("horario_sala", ""))
                for dia, horario in horarios:
                    _, turma_criada = Turma.objects.get_or_create(
                        disciplina=disciplina,
                        professor=professor,
                        dia_semana=dia,
                        horario=horario,
                    )
                    if turma_criada:
                        turmas_criadas += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"\n[Sucesso Total] Importação concluída!\n"
                    f"Páginas vasculhadas: {pagina_atual}\n"
                    f"Disciplinas no Banco: {disciplinas_criadas}\n"
                    f"Professores no Banco: {professores_criados}\n"
                    f"Vínculos de Turmas: {turmas_criadas}\n"
                )
            )

        except Exception as e:
            self.salvar_debug(driver)
            self.stdout.write(self.style.ERROR(f"\nErro crítico na execução do comando: {e}"))
            traceback.print_exc()
            driver.quit()
