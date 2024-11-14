"""
24/10/2024
@PLima

Automação PDID - Extrai em pdf todas as prescrições dos pacientes Internados
"""

import tkinter as tk
import os
import datetime
from tkinter import messagebox

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import time
import pyautogui

from mouseinfo import mouseInfo

import os
import pandas as pd
import PyPDF2

import os
import glob
import shutil

import schedule
import multiprocessing
import sys



#inicialização de variaveis globais:
diretorio_atual = ""
statusMultiprocessing = False
df = ""

df_filtrado = ""
diretorio_atual_prescricoes = ""

lista_nr_atendimento = []

lb_contador = 0

def agora_limpo():
    agora_limpo = datetime.datetime.now()
    agora_limpo = agora_limpo.strftime("%Y/%m/%d")    
    agora_limpo = agora_limpo.replace(":", "_").replace("/", "_")
    return str(agora_limpo)

def agora():
    agora = datetime.datetime.now()
    agora = agora.strftime("%Y-%m-%d %H-%M-%S")
    return str(agora)


def registrar_log(texto):
    global diretorio_atual
    global statusMultiprocessing
    #Função para registrar um texto em um arquivo de log.
    diretorio_atual = os.getcwd()
    caminho_arquivo = os.path.join(diretorio_atual, 'log.txt')
    print(f"{agora()} - {texto}\n")

    # Abre o arquivo em modo de append (adiciona texto ao final)
    with open(caminho_arquivo, 'a') as arquivo:
        arquivo.write(f"{agora()} - {texto}\n")
    
def registrar_log_cronometro(texto):
    global diretorio_atual
    global statusMultiprocessing
    #Função para registrar um texto em um arquivo de log.
    diretorio_atual = os.getcwd()
    caminho_arquivo = os.path.join(diretorio_atual, 'log_cronometro.txt')
    # Abre o arquivo em modo de append (adiciona texto ao final)
    with open(caminho_arquivo, 'a') as arquivo:
        print(f"{texto}")
        arquivo.write(f"{agora()} - {texto}\n")

def registrar_log_atend_erros(texto):
    global diretorio_atual
    global statusMultiprocessing
    #Função para registrar um texto em um arquivo de log.
    diretorio_atual = os.getcwd()
    caminho_arquivo = os.path.join(diretorio_atual, 'log_atend_erros.txt')
    # Abre o arquivo em modo de append (adiciona texto ao final)
    with open(caminho_arquivo, 'a') as arquivo:
        print(f"{texto}")
        arquivo.write(f"{agora()} - {texto}\n")
        
def excluir_arquivos_past_downloads():
    registrar_log(f'============================== excluir_arquivos_past_downloads() ==============================')
    #acessando pasta download:
    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
    registrar_log(f'Caminho da pasta downloads_path: {downloads_path}')    
    files = glob.glob(os.path.join(downloads_path, '*'))
    for f in files:
        try:
            os.remove(f)
            print(f"Arquivo {f} removido com sucesso.\n\n")
        except Exception as e:
            print(f"Não foi possível remover o arquivo {f}. Erro: {e}\n")
            
def excluir_arquivos_pasta(pasta):
  try:
    shutil.rmtree(pasta)
    print(f"A pasta {pasta} e seu conteúdo foram excluídos com sucesso.")
  except OSError as error:
    print(f"Erro ao excluir a pasta: {error}")

def mover_ultimo_pdf_para_raiz(caminho_downloads, pasta_raiz):
    registrar_log(f'============================== mover_ultimo_pdf_para_raiz({caminho_downloads}, {pasta_raiz}) ==============================') 
    # Lista todos os arquivos na pasta de downloads
    arquivos = os.listdir(caminho_downloads)    
    # Filtra apenas os arquivos PDF e ordena por data de modificação (mais recente primeiro)
    pdfs = [f for f in arquivos if f.endswith('.pdf')]
    pdfs.sort(key=lambda x: os.path.getmtime(os.path.join(caminho_downloads, x)), reverse=True) 
    if pdfs:
      # Obtém o caminho completo do último PDF
      ultimo_pdf = os.path.join(caminho_downloads, pdfs[0]) 
      # Renomeia o arquivo para "arquivo.pdf"
      novo_nome = os.path.join(caminho_downloads, "Atendimentos.pdf")
      os.rename(ultimo_pdf, novo_nome)  
      # Move o arquivo para a pasta raiz
      destino = os.path.join(pasta_raiz, "Atendimentos.pdf")
      shutil.move(novo_nome, destino)
      print(f"Arquivo movido para: {destino}")
    else:
      print("Nenhum arquivo PDF encontrado na pasta de downloads.")
    
def pdf_para_df():
    global df_filtrado
    global df
    global statusMultiprocessing
    texto_completo = ""
    
    try:
        registrar_log("******def pdf_para_df():")
    
        time.sleep(2)
        #acessando pasta download:
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        registrar_log(f'Caminho da pasta download: {downloads_path}')
        
        time.sleep(2)
        #verificando arquivos da pasta download
        files = [f for f in os.listdir(downloads_path) if f.endswith('.pdf')]
        registrar_log(f"Arquivos:\n{files}")

        time.sleep(2)
        #ultimo arquivo
        ultimo_arquivo = os.path.join(downloads_path, files[0])
        registrar_log(f"\n*****Ultimo arquivo antes de renomear: {ultimo_arquivo}")
        
        registrar_log("mover_ultimo_pdf_para_raiz(ultimo_arquivo,diretorio_atual)")
        
        time.sleep(2)
        mover_ultimo_pdf_para_raiz(downloads_path,diretorio_atual)
        
        time.sleep(2)
        renomeado_arquivo = os.path.join(diretorio_atual, 'Atendimentos.pdf')
        registrar_log(f"*****caminho_arquivo: {renomeado_arquivo}")
        
        time.sleep(2)
        ultimo_arquivo = renomeado_arquivo
        registrar_log((f"ultimo_arquivo: {ultimo_arquivo}"))
        
        #abrindo ultimo arquivo para a geracao do DF
        with open(ultimo_arquivo, 'rb') as arquivo_pdf:
            leitor_pdf = PyPDF2.PdfReader(arquivo_pdf) 
            
            # Ler todas as páginas do PDF 
            for pagina in range(len(leitor_pdf.pages)): 
                pagina_atual = leitor_pdf.pages[pagina] 
                texto = pagina_atual.extract_text() 
                texto_completo += texto + "\n"
                #print(texto_completo)
            time.sleep(2)
            linhas = texto_completo.split('\n') 
            time.sleep(2)
            dados = [linha.split() for linha in linhas if linha.strip()] 
            time.sleep(2)
            df = pd.DataFrame(dados)
            #exibindo as 5 primeiras linhas:
            print(df.head(5))
            
            #exibindo todas as linhas mas só a primeira coluna:
            print(f"\n\n\n#exibindo todas as linhas mas só a primeira coluna:\n{df}")
        #return df
    
    except Exception as erro:
        registrar_log(f'================================ pdf_para_df() \n{erro}') 
        #caso de erro, vai executar novamente o app:
        execucao()
        
def Geracao_Pdf_Atendimen():
    global statusMultiprocessing
    global df
    # ============================== Geracao_Pdf_Atendimen ==============================
    registrar_log('============================== Geracao_Pdf_Atendimen ==============================')

    #tela toda:

    driver = webdriver.Chrome()
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    try:
        registrar_log(f'(============================== Try:')
        
        driver.get("http://aplicacao.hsf.local:7070/#/login")
        registrar_log('driver.get("http://aplicacao.hsf.local:7070/#/login")')
        title = driver.title

        driver.implicitly_wait(1.5)

        # box de usuario:
        box_usuario = driver.find_element(By.XPATH, value='//*[@id="loginUsername"]')
        box_usuario.send_keys('pvplima')
        registrar_log('box_usuario')
        time.sleep(2)
        
        # box de senha:
        box_senha = driver.find_element(By.XPATH, value='//*[@id="loginPassword"]')
        box_senha.send_keys('hsf@2024')
        registrar_log('box_senha')
        time.sleep(2)
        
        # botao de login:
        bt_login = driver.find_element(By.XPATH, value='//*[@id="loginForm"]/input[3]')
        bt_login.click()
        registrar_log('bt_login')
        driver.implicitly_wait(10)
        time.sleep(10)
        
        #1107,702    
        pyautogui.click(1107,702  )
        registrar_log("click objeto invalido\npyautogui.click(1107,702)")
        time.sleep(4)

        # click no atalho de utilitários:
        bt_utilitarios = driver.find_element(By.XPATH, value='//*[@id="app-view"]/tasy-corsisf1/div/w-mainlayout/div/div/w-launcher/div/ul/li[2]')
        bt_utilitarios.click()
        registrar_log('bt_utilitarios.click()')
        time.sleep(3)

        # click no atalho de bt_impressao_relatorios:
        bt_impressao_relatorios = driver.find_element(By.XPATH, value='//*[@id="app-view"]/tasy-corsisf1/div/w-mainlayout/div/div/w-launcher/div/div/div[2]/w-apps/div/div[1]/ul/li[3]/w-feature-app/a/img')
        bt_impressao_relatorios.click()
        registrar_log('bt_impressao_relatorios.click()')
        driver.implicitly_wait(2)
        time.sleep(2)

        # click no campo para procurar o relatório 1790:
        box_codigo_rel = driver.find_element(By.XPATH, value='//*[@id="detail_1_container"]/div[1]/div/div[2]/tasy-wtextbox/div/div/input')
        box_codigo_rel.send_keys('1790')
        registrar_log("box_codigo_rel.send_keys('1790')")
        driver.implicitly_wait(2)
        time.sleep(2)

        #Pressionar Item:
        pyautogui.press('enter')
        registrar_log("pyautogui.press('enter')")
        driver.implicitly_wait(5)
        time.sleep(5)
        
        # Click no botao visualizar:
        bt_visualizar_ = driver.find_element(By.XPATH, value='//*[@id="handlebar-455491"]')
        bt_visualizar_.click()
        registrar_log("bt_visualizar_.click()")
        driver.implicitly_wait(30)
        time.sleep(30)
        
        #click apos o download
        #pyautogui.click(1810,165)
        #pyautogui.click(1781,149)
        registrar_log('pyautogui.click(1786,211)')
        pyautogui.click(1786,211)
        driver.implicitly_wait(1)
        time.sleep(2)
        
        #Pressionar Item:
        pyautogui.press('enter')
        registrar_log("Pressionar Item - pyautogui.press('enter')")
        time.sleep(15)
        
        #TODO: mudar para click
        #1711,136
        registrar_log('pyautogui.click(1711,136)')
        pyautogui.click(1711,136)
        driver.implicitly_wait(2)
        time.sleep(10)
    
    except Exception as erro:
        registrar_log(f'================================ Geracao_Pdf_Atendimen\nException Error: \n{erro}') 
        #caso de erro, vai executar novamente este bloco:
        Geracao_Pdf_Atendimen()
             
    registrar_log("=========== Geracao_Pdf_Atendimen fim ========")
    # FIM:
    statusMultiprocessing = False
    registrar_log(f"global statusMultiprocessing: {statusMultiprocessing}")
    
    # pausa dramática:
    driver.implicitly_wait(2)
    time.sleep(2)
    driver.quit()

def Geracao_Pdf_Prescricao(df_):
    global statusMultiprocessing
    global df_filtrado
    global diretorio_atual_prescricoes
    global lista_nr_atendimento
    global lb_contador
    # ============================== Geracao_Pdf_Prescricao ==============================
    registrar_log('============================== Geracao_Pdf_Prescricao ==============================')
    registrar_log(f'df_filtrado = df_\nentao df_:\n{df_}')
    df_filtrado = df_
    registrar_log(f'\ndf_filtrado:\n{df_filtrado}')
    
    lb_contador = 0
    contador = 0
    contador_linhas_df = len(df_filtrado)
    registrar_log(f'contador:{contador} - contador_linhas_df: {contador_linhas_df}')
    
    #=================================== REPETICAO #=================================== 
    try:
        registrar_log('=================================== INICIO REPETICAO =================================== ')
        for index, row in df_filtrado.iterrows():
            linha = row[0]
            lista_nr_atendimento.append(linha)
            registrar_log(f'============================== Repeticao for index, row in df_filtrado.iterrows():')
            registrar_log(f"Adicionando a lista o nr_atendimento:{linha}")
            lb_contador = linha
            registrar_log(f"lb_contador:{lb_contador} - linha:{linha}")
            
            #TODO: inserir o bloco try que gera o pdf através do nr da linha
            try:
                #registrar_log("for linha in df_filtrado.iloc[:, 0]")
                registrar_log(f"Repeticao com NR_ATENDIMENTO: {linha}")
                
                #tela toda:
                driver = webdriver.Chrome()
                options = Options()
                options.add_argument("--start-maximized")
                driver = webdriver.Chrome(options=options)
                driver.get("http://aplicacao.hsf.local:7070/#/login")
                registrar_log('driver.get("http://aplicacao.hsf.local:7070/#/login")')
                title = driver.title
                driver.implicitly_wait(1.5)
                # box de usuario:
                box_usuario = driver.find_element(By.XPATH, value='//*[@id="loginUsername"]')
                box_usuario.send_keys('pvplima')
                registrar_log('box_usuario')
                time.sleep(2)
                
                # box de senha:
                box_senha = driver.find_element(By.XPATH, value='//*[@id="loginPassword"]')
                box_senha.send_keys('hsf@2024')
                registrar_log('box_senha')
                time.sleep(2)
                # botao de login:
                bt_login = driver.find_element(By.XPATH, value='//*[@id="loginForm"]/input[3]')
                bt_login.click()
                registrar_log('bt_login')
                driver.implicitly_wait(10)
                time.sleep(5)
                
                #1107,702    
                pyautogui.click(1107,702  )
                registrar_log("click objeto invalido\npyautogui.click(1107,702)")
                time.sleep(2)
        
                #TODO: foi identificado nesse momento um erro de execucao:
                #clicar no icone do CPOE:
                bt_CPOE = driver.find_element(By.XPATH, value='//*[@id="app-view"]/tasy-corsisf1/div/w-mainlayout/div/div/w-launcher/div/div/div[1]/w-apps/div/div[1]/ul/li[2]/w-feature-app/a/img')
                bt_CPOE.click()
                registrar_log('clicar no icone do CPOE:')
                driver.implicitly_wait(20)
                time.sleep(30)
                                
                #nr_atendimento
                driver.implicitly_wait(1.5)
                pyautogui.write(linha)
                registrar_log(f'nr_atendimento: {linha}')
                driver.implicitly_wait(3)
                time.sleep(5)
                #enter
                pyautogui.press('enter')
                registrar_log('1 - enter')
                driver.implicitly_wait(3)
                time.sleep(5)
                #enter
                pyautogui.press('enter')
                registrar_log('2 - enter')
                driver.implicitly_wait(15)
                time.sleep(15)
                #click atendimento fechado
                pyautogui.click(1100,709)
                registrar_log("click atendimento fechado")
                driver.implicitly_wait(3)
                time.sleep(3)
                #botao visualizar
                bt_cpoe_relatorios = driver.find_element(By.XPATH, value='//*[@id="handlebar-40"]')
                bt_cpoe_relatorios.click()
                registrar_log("bt_cpoe_relatorios.click()")
                driver.implicitly_wait(1)
                time.sleep(2)
                
                #botao visualizar
                bt_cpoe_visualizar = driver.find_element(By.XPATH, value='//*[@id="popupViewPort"]/li[5]/div[3]')
                bt_cpoe_visualizar.click()
                registrar_log("bt_cpoe_visualizar")
                driver.implicitly_wait(12)
                time.sleep(12)
                
                #click apos o download
                #pyautogui.click(1810,165)
                #pyautogui.click(1781,149)
                pyautogui.click(1786,211)
                driver.implicitly_wait(1)
                time.sleep(2)
                
                #Pressionar Item:
                pyautogui.press('enter')
                registrar_log("Pressionar Item\npyautogui.press('enter')")
                time.sleep(3)
                            
                registrar_log("9x tab - inicio")
                pyautogui.press('tab')
                pyautogui.press('tab')
                pyautogui.press('tab')
                pyautogui.press('tab')
                pyautogui.press('tab')
                pyautogui.press('tab')
                pyautogui.press('tab')
                pyautogui.press('tab')
                pyautogui.press('tab')
                registrar_log("9x tab - fim")
                time.sleep(3)
                
                #Pressionar Item:
                pyautogui.press('enter')
                registrar_log("Pressionar Item\npyautogui.press('enter')")
                time.sleep(3)
                
                registrar_log("5x tab - inicio")
                pyautogui.press('tab')
                pyautogui.press('tab')
                pyautogui.press('tab')
                pyautogui.press('tab')
                pyautogui.press('tab')
                registrar_log("5x tab - fim")
                driver.implicitly_wait(1)
                time.sleep(3)
                
                #Pressionar Item:
                pyautogui.press('enter')
                registrar_log("Pressionar Item\npyautogui.press('enter')")
                time.sleep(3)
        
                #Pressionar Item:
                pyautogui.press('enter')
                registrar_log("Pressionar Item\npyautogui.press('enter') 1")
                time.sleep(2)
                #acessando pasta download:
                downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
                registrar_log(f'Caminho da pasta download: {downloads_path}')
                time.sleep(2)
                
                #verificando arquivos da pasta download
                files = [f for f in os.listdir(downloads_path) if f.endswith('.pdf')]
                registrar_log(f"Arquivos:\n{files}")
                time.sleep(2)
                #ultimo arquivo
                ultimo_arquivo = os.path.join(downloads_path, files[0])
                registrar_log(f"\n*****Ultimo arquivo antes de renomear: {ultimo_arquivo}")
                time.sleep(2)
                
                # Caminho da pasta Prescricoes
                #data_hora = agora_limpo()
                pasta_prescricoes = "Prescricoes"
                registrar_log(f"pasta_prescricoes: {pasta_prescricoes}")
                time.sleep(2)
                
                pasta_data = os.path.join(pasta_prescricoes, agora_limpo())
                registrar_log(f"pasta_data: {pasta_data}")
                time.sleep(2)
                # Cria a pasta da data se não existir
                os.makedirs(pasta_data, exist_ok=True)
                registrar_log(f"***********os.makedirs: {pasta_data}")
                time.sleep(2)
                #renomeia e move os arquivos
                registrar_log(f"Data_hora: {agora()}")
                caminho_antigo = os.path.join(downloads_path, ultimo_arquivo)
                registrar_log(f"caminho antigo: {caminho_antigo}")
                nr_atendimento = linha
                caminho_novo = os.path.join(pasta_data, f"{nr_atendimento} - {agora()}.pdf")
                registrar_log(f'caminho_novo = {caminho_novo},\narquivo:{agora()}.pdf)')
            
                try:
                    time.sleep(2)
                    shutil.move(caminho_antigo, caminho_novo)
                    registrar_log(f"Arquivo {caminho_novo} renomeado e movido com sucesso.")
                except shutil.Error as e:
                    registrar_log(f"Erro ao mover o arquivo: {e}")
                    
                time.sleep(2)
                #FIM
                contador += 1
                #se rodar tudo ok, retirar o número de atendimento da lista_nr_atendimento
                lista_nr_atendimento.remove(linha)
                registrar_log(f'lista_nr_atendimento.remove({linha})')
                registrar_log(f'Retirando da lista o nr_atendimento: {linha}')
                registrar_log(f'lista_nr_atendimento:\n{lista_nr_atendimento}\n')
                registrar_log(f'\ncontador = {contador} - de contador_linhas_df:{contador_linhas_df}')
                registrar_log(f'\n********************FIM********************\n')
                
                # pausa dramática:
                time.sleep(2)
                driver.quit()
                
            except Exception as erro:
                    registrar_log(f'=========== \nERROR:\nexcept do try de dento do for linha in df_filtrado')
                    registrar_log('\nlista_nr_atendimento:{lista_nr_atendimento}\ncontador: {contador} \n{erro}')
                    copiar_arquivos()
    
    except Exception as erro:
        #ao terminar extoura um exception e cai nesse bloco
        registrar_log(f"=========== \nERROR:\n except: for linha in df_filtrado:\nlista_nr_atendimento:{lista_nr_atendimento}\ncontador: {contador} \n{erro}")
        #tenho que apagar todos os atendimentos até o que deu erro, que é o linha
        copiar_arquivos()        
            
             
    registrar_log(f'Lista com nr_atendimentos com erro\nlista_nr_atendimento: {lista_nr_atendimento}')
    #montar data frame com lista de itens que tiveram erro e não foram deletados:
    df_lista_nr_atendimento = pd.DataFrame(lista_nr_atendimento)
    registrar_log(f'df_lista_nr_atendimento: \n{df_lista_nr_atendimento}')
    
    #ação para o caso do df_lista_nr_atendimento for vazio ou não:
    if df_lista_nr_atendimento.empty:
        registrar_log(f'\nTodos os atendimentos foram gerados com sucesso!')
        registrar_log(f'\n=========== FIM Geracao_Pdf_Prescricao()\n\n\n\n\n')
        df_lista_nr_atendimento = None
        df = df_lista_nr_atendimento
        registrar_log(f'if df_lista_nr_atendimento.empty:\ndf_lista_nr_atendimento:{df_lista_nr_atendimento}\df:{df}')
    else:
        registrar_log(f'df_lista_nr_atendimento nao esta em branco\nglobal df recebera df_lista_nr_atendimento!!!!')
        registrar_log(f'\ndf = df_lista_nr_atendimento: \n{df_lista_nr_atendimento}')
        df = df_lista_nr_atendimento
        df_lista_nr_atendimento = None
        registrar_log(f'df_lista_nr_atendimento.clear(){df_lista_nr_atendimento}\n')
        registrar_log(f'df = df: \n{df}')
        registrar_log_atend_erros(df)
        registrar_log(f"Executara novamente a Geracao_Pdf_Prescricao() com o global df apenas com os nr_atendimento que tiveram erros:\n{df}")
        Geracao_Pdf_Prescricao(df)
    
    """
    #TODO: Apos o erro ele segue com a execucao e precisa agora rodar novamente na hora pre determinda
    registrar_log('\nFinal do for linha\ndriver.implicitly_wait(10)')
    #driver.implicitly_wait(10)
    
    # copiar_arquivos:
    registrar_log(f'def Geracao_PDF_Prescricao() bloco com funcao copiar_arquivos()')
    copiar_arquivos()

    """     
    # FIM:
    statusMultiprocessing = False
    registrar_log(f'statusMultiprocessing = {statusMultiprocessing}')

def cronometro_tarefa_agendada():
    registrar_log(f'"============================== cronometro_tarefa_agendada() "==============================')
    #agendamentos:
    schedule.every().day.at("00:05:00").do(execucao)
    registrar_log(f'schedule.every().day.at("00:05:00").do(execucao)')
    #schedule.every().day.at("14:00:00").do(execucao)
    #schedule.every().day.at("14:40:00").do(execucao)
    #inserindo o schedule
    while True:
        schedule.run_pending()
        time.sleep(1)
        registrar_log_cronometro(f'{agora()} - schedule.run_pending()')

def copiar_arquivos():
    origem = "C:\\Pietro\\Projetos\\RPA_PRESCR_EM_PDF\\Prescricoes"
    destino = "\\\\192.168.103.252\\tihsf$\\PIETRO\\Projetos\\RPA_PRESCR_EM_PDF\\Prescricoes"
    """Copia todos os arquivos e subdiretórios de uma pasta para outra.

    Args:
      origem: Caminho completo da pasta de origem.
      destino: Caminho completo da pasta de destino.
    """
    registrar_log(f'============================== def copiar_arquivos() ==============================')

    try:
        registrar_log(f'"============================== copiar_arquivos() Try:\nshutil.copytree(origem, destino, dirs_exist_ok=True)')
        shutil.copytree(origem, destino, dirs_exist_ok=True)
        registrar_log(f"\nArquivos copiados com sucesso \nde: {origem} \npara {destino}\n============================== FIM copiar_arquivos()")
    except FileExistsError:
        registrar_log(f"\nA pasta de destino {destino} ja existe. Verifique se deseja sobrescrever.\n============================== FileExistsError copiar_arquivos()")
    except Exception as e:
        registrar_log(f"Ocorreu um erro durante a cópia: {str(e)}\n============================== Exception copiar_arquivos()")

def execucao():
    global statusMultiprocessing
    global df
    global lb_contador
    registrar_log("============================== execucao() ========================")
    registrar_log(f"Tarefa inicializada!\nstatusMultiprocessing:{statusMultiprocessing}\ndf:{df}\nlb_contador:{lb_contador}")
    
    #============================== execucao ========================
    #deletando todos os arquivos da pasta Prescricoes
    #excluir_arquivos_pasta("Prescricoes")
    excluir_arquivos_past_downloads()
    Geracao_Pdf_Atendimen()
    pdf_para_df()
    registrar_log(f'\ndf:\n{df}\n')
    Geracao_Pdf_Prescricao(df)    
    
    
def interface_grafica():
    registrar_log("============================== interface_grafica()")
    global lb_contador
    
    
    def ao_fechar():
        resultado = messagebox.askyesno("Confirmação", "Tem certeza de que deseja fechar o aplicativo?")
        if resultado:
            # Feche o aplicativo
            janela.destroy()
        """Função chamada quando o usuário clica no botao 'X' para fechar a janela."""
        registrar_log("O aplicativo foi fechado no botao X\n")
        
    def iniciar():
        global statusMultiprocessing
        global df_filtrado
        global df
        registrar_log("============================== def iniciar()")
        registrar_log(f"Botao Iniciar clicado! \nglobal statusMultiprocessing: {statusMultiprocessing}")

        if statusMultiprocessing:
            registrar_log(f"Thread já foi iniciada!")
            messagebox.showinfo("Tarefa já incializada!")

        else:
            statusMultiprocessing = True                       
            registrar_log('==================================== def iniciar() ====================================')            
            #TODO: colocar dentro da execucao que usa o multiprocessing
            processo = multiprocessing.Process(target=cronometro_tarefa_agendada)
            processo.start()
            label_status['text'] = "Tarefa Agendada Inicializada!"  
            
    def executar():
        global statusMultiprocessing
        global df_filtrado
        global df
        global lb_contador
        registrar_log("============================== def executar()")
        registrar_log(f"Botao executar clicado! \nglobal statusMultiprocessing: {statusMultiprocessing}\nlb_contador:{lb_contador}")

        if statusMultiprocessing:
            registrar_log(f"Thread já foi iniciada!")
            messagebox.showinfo("Tarefa já incializada!")

        else:
            statusMultiprocessing = True                       
            registrar_log('==================================== def iniciar() ====================================')            
            #TODO: colocar dentro da execucao que usa o multiprocessing
            processo = multiprocessing.Process(target=execucao)
            processo.start()
            label_status['text'] = "Tarefa planejada inicializada!"
    
    def fechar():
        registrar_log(f"\n\n{agora()}def fechar() - \njanela.destroy()\nsys.exit()")
        # Exiba uma caixa de diálogo de confirmação
        #resultado = messagebox.askyesno("Confirmação", "Tem certeza de que deseja fechar o aplicativo?")
        #if resultado:
        #    # Feche o aplicativo
        #    registrar_log("janela.destroy()")
        #    janela.destroy()
        janela.destroy()
        sys.exit()

    #INTERFACE GRAFICA:
    janela = tk.Tk()
    janela.maxsize(600,400)
    janela.geometry('600x400')
    janela.title("RPA PRESCRICOES POR SETOR")
    
    # Associa a função ao_fechar ao evento de fechamento da janela
    janela.protocol("WM_DELETE_WINDOW", ao_fechar)
    
    # Rótulo para mostrar o status
    label_status = tk.Label(janela, text="Tarefa não iniciada!")
    label_status.place(x=210 , y=105)
    
    bt_Iniciar = tk.Button(janela, width=18, text="Tarefa Planejada",command=lambda: [
        #TODO: TESTAR ETAPAS DO SISTEMA ABAIXO
        iniciar()
    ])
    bt_Iniciar.place(x=80 , y=215)

    bt_executar = tk.Button(janela, width=18, text="Executar tarefa", command=lambda: [executar()])
    bt_executar.place(x=350 , y=215)
    
    janela.mainloop()

    
    
if __name__ == "__main__":
    try:
        registrar_log(f'\n\n\n\n\n\n\n\n{agora()} ================================ __name__ == "__main__" ================================\n')
                
        #deletando todos os arquivos da pasta download
        pasta_downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        
        interface_grafica() 
            
    except Exception as erro:
        registrar_log(f'================================ if __name__ == "__main__"\nException Error: \n{erro}')