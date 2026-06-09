from pathlib import Path

content = r'''from django.core.management.base import BaseCommand
from core.models import Disciplina, Professor
import pandas as pd
import time
from io import StringIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

class Command(BaseCommand):
    help = "Importa disciplinas e professores do MicroHorário diretamente para o banco."

    def handle(self, *args, **kwargs):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")

        driver = webdriver.Chrome(options=options)

        url = "https://microhorario.rdc.puc-rio.br/WebMicroHorarioConsulta/MicroHorarioConsulta.aspx?sessao=U2lzdGVtYT1QVUNPTkxJTkVfQUxVTk8mQXBsaWNhY2FvPU1JQ1JPX0hPUkFSSU8mRnVuY2FvPUNPTlNVTFRBJklEPTBhODJkN2MxODEzZjQxZTY5ZTQ1MTNhNmQxY2I4Yzdk"

        self.stdout.write("Abrindo MicroHorário...")
        driver.get(url)
        time.sleep(3)

        try:
            try:
                botao = driver.find_element(
                    By.XPATH,
                    "//a[contains(text(),'Buscar') or contains(text(),'Consultar')]"
                )
            except Exception:
                botao = driver.find_element(
                    By.XPATH,
                    "//input[@type='submit' or @value='Buscar']"
                )

            botao.click()
            time.sleep(4)

        except Exception as e:
            driver.quit()
            raise Exception(f"Erro ao iniciar consulta: {e}")

        todos_os_dfs = []
        pagina_atual = 1

        while True:

            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")

            tabela_encontrada = False

            for tabela in soup.find_all("table"):
                try:
                    dfs = pd.read_html(StringIO(str(tabela)))

                    if dfs and len(dfs[0].columns) >= 10:
                        df = dfs[0].iloc[:, :10]

                        df.columns = [
                            "Disciplina",
                            "codigo",
                            "nome",
                            "professor",
                            "credito",
                            "",
                            "",
                            "",
                            "",
                            "horario_sala",
                        ]

                        todos_os_dfs.append(df)
                        tabela_encontrada = True
                        break

                except Exception:
                    pass

            if not tabela_encontrada:
                self.stdout.write(
                    self.style.WARNING(
                        f"Nenhuma tabela encontrada na página {pagina_atual}"
                    )
                )

            proxima = pagina_atual + 1

            try:
                link = driver.find_element(By.XPATH, f"//a[text()='{proxima}']")
                driver.execute_script(
                    "arguments[0].scrollIntoView();",
                    link
                )
                time.sleep(0.5)
                link.click()

                pagina_atual = proxima
                time.sleep(4)

            except Exception:
                try:
                    link = driver.find_element(
                        By.XPATH,
                        f"//a[contains(@href, 'Page${proxima}')]"
                    )

                    driver.execute_script(
                        "arguments[0].scrollIntoView();",
                        link
                    )

                    link.click()
                    pagina_atual += 1
                    time.sleep(4)

                except Exception:
                    break

        driver.quit()

        if not todos_os_dfs:
            self.stdout.write(self.style.ERROR("Nenhum dado coletado."))
            return

        df_final = pd.concat(todos_os_dfs, ignore_index=True)

        df_final["Disciplina"] = df_final["Disciplina"].astype(str)
        df_final["codigo"] = df_final["codigo"].astype(str)

        df_final = df_final[
            ~df_final["Disciplina"].str.contains("Disciplina", na=False)
        ]

        palavras = ["Último", "Primeiro", "<<", ">>", "antigos"]

        for palavra in palavras:
            df_final = df_final[
                ~df_final["Disciplina"].str.contains(
                    palavra,
                    na=False,
                    case=False
                )
            ]

            df_final = df_final[
                ~df_final["codigo"].str.contains(
                    palavra,
                    na=False,
                    case=False
                )
            ]

        df_final = df_final[
            df_final["codigo"].str.strip().str.len() > 3
        ]

        df_final["nome"] = df_final["nome"].astype(str).str.strip()
        df_final["codigo"] = df_final["codigo"].astype(str).str.strip()

        df_final.replace("", pd.NA, inplace=True)
        df_final = df_final.dropna(subset=["nome", "codigo"])
        df_final = df_final.loc[:, df_final.columns != ""]

        disciplinas_criadas = 0
        professores_criados = 0

        for _, row in df_final.iterrows():

            professor_nome = str(
                row.get("professor", "Não informado")
            ).strip()

            if not professor_nome:
                professor_nome = "Não informado"

            professor, prof_created = Professor.objects.get_or_create(
                nome=professor_nome,
                defaults={
                    "departamento": "Não informado"
                }
            )

            if prof_created:
                professores_criados += 1

            try:
                creditos = int(float(row.get("credito", 0)))
            except Exception:
                creditos = 0

            _, disc_created = Disciplina.objects.update_or_create(
                codigo=str(row["codigo"]).strip(),
                defaults={
                    "nome": str(row["nome"]).strip(),
                    "creditos": creditos,
                    "periodo": 0,
                }
            )

            if disc_created:
                disciplinas_criadas += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Importação concluída. "
                f"{disciplinas_criadas} disciplinas criadas, "
                f"{professores_criados} professores criados."
            )
        )
'''

path = "/mnt/data/importar_microhorario.py"
Path(path).write_text(content, encoding="utf-8")

print(path)
