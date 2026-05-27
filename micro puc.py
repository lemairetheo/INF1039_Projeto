import time
from io import StringIO
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup

# ==============================================================================
# PASSO 1: CONFIGURAR E ABRIR O SITE NO NAVEGADOR
# ==============================================================================

# Configura o navegador Chrome para rodar em "headless" (em segundo plano, sem abrir a janela na tela)
options = webdriver.ChromeOptions()
#options.add_argument("--headless")  
driver = webdriver.Chrome(options=options)

print("Acessando a página do Microhorário da PUC...")
url = "https://microhorario.rdc.puc-rio.br/WebMicroHorarioConsulta/MicroHorarioConsulta.aspx?sessao=U2lzdGVtYT1QVUNPTkxJTkVfQUxVTk8mQXBsaWNhY2FvPU1JQ1JPX0hPUkFSSU8mRnVuY2FvPUNPTlNVTFRBJklEPTBhODJkN2MxODEzZjQxZTY5ZTQ1MTNhNmQxY2I4Yzdk"

# Abre o link e espera 3 segundos para garantir que a página carregou a estrutura inicial
driver.get(url)
time.sleep(3)

try:
    print("Tentando clicar no botão 'Buscar' para listar todas as disciplinas...")
   
    # Estratégia 1: Tenta achar o botão se ele for um link (tag <a>) que diz 'Buscar' ou 'Consultar'
    try:
        botao_buscar = driver.find_element(By.XPATH, "//a[contains(text(), 'Buscar') or contains(text(), 'Consultar')]")
    # Estratégia 2: Se falhar, procura por um botão de clique tradicional (tag <input>) com o texto 'Buscar'
    except:
        botao_buscar = driver.find_element(By.XPATH, "//input[@type='submit' or @value='Buscar']")
       
    # Dá o clique no botão para disparar a busca no site
    botao_buscar.click()
    print("Botão clicado com sucesso! Iniciando a varredura das páginas...")
   
    # Aguarda 4 segundos para o servidor processar o clique e desenhar a tabela na tela
    time.sleep(4)

except Exception as e:
    print(f"\n[Erro Inicial] Não foi possível iniciar a busca no site: {e}")
    driver.quit()
    exit()

# ==============================================================================
# PASSO 2: LOOP PARA COLETAR OS DADOS PÁGINA POR PÁGINA (ATÉ A PÁGINA 204)
# ==============================================================================

todos_os_dfs = []    # Lista vazia que vai guardar os dados de cada página coletada
pagina_atual = 1     # Contador para sabermos em qual página o robô está trabalhando


while True:
    print(f"Lendo e processando os dados da página {pagina_atual} ...")
   
    # Pega o código HTML atualizado da página onde o navegador está parado agora
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
   
    # Encontra todas as tabelas presentes no código desse HTML
    tabelas_html = soup.find_all('table')
   
    tabela_encontrada = False
    for tab in tabelas_html:
        # Usa o Pandas para converter a tabela HTML em uma tabela de dados (DataFrame)
        df_lista = pd.read_html(StringIO(str(tab)))
       
        # Se a tabela tiver dados reais (detectado se ela tem 10 ou mais colunas)
        if df_lista and len(df_lista[0].columns) >= 10:
            # Pega as 10 primeiras colunas e dá nomes organizados para elas
            df_pagina = df_lista[0].iloc[:, :10]
            df_pagina.columns = ["Disciplina", "codigo", "nome", "professor", "credito", "", "", "", "", "horario_sala"]
           
            # Guarda essa tabela da página atual na nossa lista geral
            todos_os_dfs.append(df_pagina)
            tabela_encontrada = True
            break # Sai deste mini-loop e vai para a lógica de paginação
           
    if not tabela_encontrada:
        print(f"Aviso: Nenhuma tabela de disciplinas foi detectada na página {pagina_atual}.")

   

    # --- LÓGICA DE NAVEGAÇÃO: IR PARA A PRÓXIMA PÁGINA ---
    proxima_pagina = pagina_atual + 1
    try:
        # Busca na tela o link do próximo número (Ex: se está na 1, procura pelo link texto '2')
        link_proxima = driver.find_element(By.XPATH, f"//a[text()='{proxima_pagina}']")
        print(f"Encontrei o link e vou clicar")
       
        # Faz a tela rolar até o botão aparecer (evita erros do botão estar escondido)
        driver.execute_script("arguments[0].scrollIntoView();", link_proxima)
        print(f"Scrollei a página pra não me bugar")
        time.sleep(0.5)
       
        # Clica no número da próxima página
        link_proxima.click()
        print(f"Cliquei no link da próxima")
       
        # Atualiza o nosso contador e espera 4 segundos para os novos dados carregarem na tela
        pagina_atual = proxima_pagina
        print(f"Fui para a página {pagina_atual}")
        time.sleep(4)
       
    except:
        # Caso ele não ache o número seguinte, pode ser porque mudou o bloco de páginas (ex: passou da página 10)
        # Aí tentamos clicar no botão de reticências '...' que carrega os próximos números
        try:
            link_reticencias = driver.find_element(By.XPATH, f"//a[contains(@href, \"Page${proxima_pagina}\")]")
            print(f"Não encontrei o link, então vou clicar em '...'")
            driver.execute_script("arguments[0].scrollIntoView();", link_reticencias)
            link_reticencias.click()
            print(f"Cliquei no link do '...'")
           
            # Avança o contador e aguarda o carregamento do novo bloco de páginas
            pagina_atual += 1
            print(f"Fui para a página {pagina_atual}")
            time.sleep(4)
        except:
            # Se nem o próximo número nem as reticências existirem, a paginação do site acabou de verdade
            print("\nChegamos ao fim definitivo de todas as páginas do site antes do limite!")
            break

# Fecha o navegador oculto, pois já coletamos todo o conteúdo necessário
driver.quit()

# ==============================================================================
# PASSO 3: LIMPEZA DOS DADOS E GERACÃO DO ARQUIVO CSV
# ==============================================================================
if todos_os_dfs:
    print("\nIniciando o processo de limpeza dos dados coletados...")
   
    # Junta todas as tabelas de todas as páginas em uma única tabelona gigante
    df_final = pd.concat(todos_os_dfs, ignore_index=True)
   
    # Garante que as colunas chaves sejam tratadas puramente como texto
    df_final["Disciplina"] = df_final["Disciplina"].astype(str)
    df_final["codigo"] = df_final["codigo"].astype(str)
   
    # FILTRO 1: Remove linhas que continham cabeçalhos repetidos no meio da tabela
    df_final = df_final[df_final["Disciplina"].str.contains("Disciplina", na=False) == False]
   
    # FILTRO 2: Remove as linhas de sujeira da paginação que vinham escrito "Primeiro", "Último", "<<", etc.
    palavras_para_remover = ["Último", "Primeiro", "<<", ">>", "antigos"]
    for palavra in palavras_para_remover:
        df_final = df_final[df_final["Disciplina"].str.contains(palavra, na=False, case=False) == False]
        df_final = df_final[df_final["codigo"].str.contains(palavra, na=False, case=False) == False]
   
    # FILTRO 3: Remove linhas onde o código da disciplina ficou preenchido apenas com os números órfãos da paginação.
    # Disciplinas reais da PUC têm códigos maiores (ex: 'ADM1001' tem 7 letras/números). Se tiver menos de 3, é descartado.
    df_final = df_final[df_final["codigo"].str.strip().str.len() > 3]
   
    # FILTRO 4: Limpa espaços em branco invisíveis e substitui textos totalmente vazios ("") por nulos oficiais do Pandas (NaN)
    df_final["nome"] = df_final["nome"].astype(str).str.strip()
    df_final["codigo"] = df_final["codigo"].astype(str).str.strip()
    df_final.replace("", pd.NA, inplace=True)
   
    # FILTRO 5: Deleta permanentemente qualquer linha onde a coluna 'nome' ou 'codigo' estejam nulas/em branco
    df_final = df_final.dropna(subset=["nome", "codigo"])
   
    # FILTRO 6: Deleta aquelas colunas vazias sem título que criamos no mapeamento de colunas inicial (colunas extras)
    df_final = df_final.loc[:, df_final.columns != ""]
   
    # Salva o resultado final em um arquivo excel/csv configurado para o padrão do Excel brasileiro (utf-8-sig)
    df_final.to_csv("microhorario_puc_completo.csv", index=False, encoding="utf-8-sig")
    print(f"\nSucesso total! Processo finalizado com {pagina_atual} páginas coletadas.")
    print("O arquivo limpo e organizado foi salvo com o nome: 'microhorario_puc_completo.csv'.")
else:
    print("\nNenhum dado pôde ser extraído do site. O arquivo não foi gerado.")
