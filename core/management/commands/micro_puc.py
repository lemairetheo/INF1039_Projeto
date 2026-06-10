import re
import time
from io import StringIO
from django.core.management.base import BaseCommand
from core.models import Disciplina, Professor, Turma
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

DIAS_MAP = {
    "2": "SEG",
    "3": "TER",
    "4": "QUA",
    "5": "QUI",
    "6": "SEX",
    "7": "SAB",
}


def extrair_dias_horarios(texto):
    """Extrai pares (dia, horario) da string de horário do MicroHorário.

    Exemplos: 2ABCD -> [('SEG', 'ABCD')]
    """
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
    help = "Importa disciplinas, professores e turmas do MicroHorário diretamente para o banco."

    def handle(self, *args, **options):
        # Configuração do Selenium Headless
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=chrome_options)

        url = (
            "https://microhorario.rdc.puc-rio.br/WebMicroHorarioConsulta/"
            "MicroHorarioConsulta.aspx?sessao="
            "U2lzdGVtYT1QVUNPTkxJTkVfQUxVTk8mQXBsaWNhY2FvPU1JQ1JPX0hPUkFSSU8m"
            "RnVuY2FvPUNPTlNVTFRBJklEPTBhODJkN2MxODEzZjQxZTY5ZTQ1MTNhNmQxY2I4Yzdk"
        )

        self.stdout.write("Abrindo MicroHorário...")
        driver.get(url)
        time.sleep(3)

        # Clica no botão de Buscar/Consultar
        try:
            try:
                botao = driver.find_element(
                    By.XPATH,
                    "//a[contains(text(),'Buscar') or contains(text(),'Consultar')]",
                )
            except Exception:
                botao = driver.find_element(
                    By.XPATH, "//input[@type='submit' or @value='Buscar']"
                )

            botao.click()
            self.stdout.write("Consulta iniciada, coletando dados...")
            time.sleep(4)
        except Exception as e:
            driver.quit()
            self.stdout.write(
                self.style.ERROR(f"Erro ao iniciar consulta: {e}")
            )
            return

        todos_os_dfs = []
        pagina_atual = 1

        while True:
            self.stdout.write(f"Raspando página {pagina_atual}...")
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            tabela_encontrada = False

            for tabela in soup.find_all("table"):
                try:
                    dfs = pd.read_html(StringIO(str(tabela)))
                    if dfs and len(dfs[0].columns) >= 10:
                        # Pega as 10 colunas relevantes
                        df = dfs[0].iloc[:, :10].copy()

                        # Força a renomeação correta mapeando o HTML da PUC
                        df.columns = [
                            "codigo_turma",  # Coluna 0 (Ex: INF1001)
                            "codigo",  # Coluna 1 (Normalmente igual ou sub-código)
                            "nome",  # Coluna 2 (Nome da matéria)
                            "professor",  # Coluna 3
                            "credito",  # Coluna 4
                            "vagas",
                            "inscritos",
                            "status",
                            "horario_sala",  # Coluna 8 ou 9 dependendo da variação
                            "extra",
                        ]

                        todos_os_dfs.append(df)
                        tabela_encontrada = True
                        break
                except Exception:
                    pass

            if not tabela_encontrada:
                self.stdout.write(
                    self.style.WARNING(
                        f"Nenhuma tabela válida na página {pagina_atual}"
                    )
                )

            # Lógica de Paginação (Próxima Página)
            proxima = pagina_atual + 1
            try:
                link = driver.find_element(By.XPATH, f"//a[text()='{proxima}']")
                driver.execute_script(
                    "arguments[0].scrollIntoView();", link
                )
                time.sleep(0.5)
                link.click()
                pagina_atual = proxima
                time.sleep(4)
            except Exception:
                try:
                    link = driver.find_element(
                        By.XPATH, f"//a[contains(@href, 'Page${proxima}')]"
                    )
                    driver.execute_script(
                        "arguments[0].scrollIntoView();", link
                    )
                    link.click()
                    pagina_atual = proxima
                    time.sleep(4)
                except Exception:
                    self.stdout.write("Fim das páginas encontradas.")
                    break

        driver.quit()

        if not todos_os_dfs:
            self.stdout.write(self.style.ERROR("Nenhum dado coletado."))
            return

        # Tratamento dos Dados no Pandas
        df_final = pd.concat(todos_os_dfs, ignore_index=True)
        df_final["codigo_turma"] = df_final["codigo_turma"].astype(str)
        df_final["codigo"] = df_final["codigo"].astype(str)

        # Limpeza de lixo de paginação e topo de tabela
        df_final = df_final[
            ~df_final["codigo_turma"].str.contains(
                "Disciplina|Último|Primeiro|<<|>>", na=False, case=False
            )
        ]
        df_final = df_final[
            df_final["codigo_turma"].str.strip().str.len() >= 3
        ]

        df_final["nome"] = df_final["nome"].astype(str).str.strip()
        df_final.dropna(subset=["nome", "codigo_turma"], inplace=True)

        # Contadores para o relatório final
        disciplinas_criadas = 0
        professores_criados = 0
        turmas_criadas = 0

        self.stdout.write("Salvando os dados no Banco de Dados...")

        # Loop de Inserção no Django ORM
        for _, row in df_final.iterrows():
            # 1. Trata Professor
            professor_nome = str(
                row.get("professor", "Não informado")
            ).strip()
            if not professor_nome or professor_nome.lower() == "nan":
                professor_nome = "Não informado"

            professor, prof_created = Professor.objects.get_or_create(
                nome=professor_nome,
                defaults={"departamento": "Não informado"},
            )
            if prof_created:
                professores_criados += 1

            # 2. Trata Créditos
            try:
                creditos = int(float(row.get("credito", 0)))
            except Exception:
                creditos = 0

            # 3. Trata Disciplina (Usa o código limpo da matéria)
            cod_disciplina = str(row["codigo_turma"]).strip()

            disciplina, disc_created = Disciplina.objects.update_or_create(
                codigo=cod_disciplina,
                defaults={
                    "nome": str(row["nome"]).strip(),
                    "creditos": creditos,
                    "periodo": 0,
                },
            )
            if disc_created:
                disciplinas_criadas += 1

            # 4. Trata Turma (Quebra horários múltiplos, ex: 2ABCD 4EFGH)
            horarios = extrair_dias_horarios(row.get("horario_sala", ""))

            for dia_semana, horario in horarios:
                # Evita duplicar exatamente a mesma combinação
                _, turma_created = Turma.objects.get_or_create(
                    disciplina=disciplina,
                    professor=professor,
                    dia_semana=dia_semana,
                    horario=horario,
                )
                if turma_created:
                    turmas_criadas += 1

        # Feedback Final de Sucesso no Terminal
        self.stdout.write(
            self.style.SUCCESS(
                f"\n[OK] Importação concluída com sucesso!\n"
                f"- {disciplinas_criadas} novas disciplinas adicionadas/atualizadas.\n"
                f"- {professores_criados} novos professores cadastrados.\n"
                f"- {turmas_criadas} novos horários de turmas criados."
            )
        )
