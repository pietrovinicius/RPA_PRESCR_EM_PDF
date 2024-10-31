import tkinter as tk
import os
import datetime
import threading
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


#inicialização de variaveis globais:
diretorio_atual = ""
statusThread = False
df = ""

df_filtrado = ""


def agora_limpo():
    agora_limpo = datetime.datetime.now()
    agora_limpo = agora_limpo.strftime("%d/%m/%Y %H:%M:%S")
    #agora_limpo = agora_limpo.replace(":", "_").replace("/", "_")
    return str(agora_limpo)

def registrar_log(texto):
    global diretorio_atual
    #Função para registrar um texto em um arquivo de log.
    diretorio_atual = os.getcwd()
    caminho_arquivo = os.path.join(diretorio_atual, 'log.txt')
    print(f"{agora_limpo()} - {texto}\n")

    # Abre o arquivo em modo de append (adiciona texto ao final)
    with open(caminho_arquivo, 'a') as arquivo:
        arquivo.write(f"{agora_limpo()} - {texto}\n")
    
def delete_all_files_in_directory(directory):
    registrar_log(f"delete_all_files_in_directory({directory})")
    files = glob.glob(os.path.join(directory, '*'))
    for f in files:
        try:
            os.remove(f)
            print(f"Arquivo {f} removido com sucesso.")
        except Exception as e:
            print(f"Não foi possível remover o arquivo {f}. Erro: {e}")

def mover_ultimo_pdf_para_raiz(caminho_downloads, pasta_raiz):
  """
  Move o último arquivo PDF encontrado na pasta de downloads para a pasta raiz da aplicação.

  Args:
    caminho_downloads: Caminho absoluto para a pasta de downloads.
    pasta_raiz: Caminho absoluto para a pasta raiz da aplicação.
  """

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
    
    
def pdf_para_csv():
    global df_filtrado
    global df
    global statusThread
    texto_completo = ""
    
    registrar_log("******def pdf_para_csv():")
    
    #acessando pasta download:
    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
    registrar_log(f'Caminho da pasta download: {downloads_path}')
    
    #verificando arquivos da pasta download
    files = [f for f in os.listdir(downloads_path) if f.endswith('.pdf')]
    registrar_log(f"Arquivos:\n{files}")

    #ultimo arquivo
    ultimo_arquivo = os.path.join(downloads_path, files[0])
    registrar_log(f"\n*****Ultimo arquivo antes de renomear: {ultimo_arquivo}")
    
    registrar_log("mover_ultimo_pdf_para_raiz(ultimo_arquivo,diretorio_atual)")
    mover_ultimo_pdf_para_raiz(downloads_path,diretorio_atual)
    
    caminho_arquivo = os.path.join(diretorio_atual, 'Atendimentos.pdf')
    
    registrar_log(f"*****caminho_arquivo: {caminho_arquivo}")
    
    ultimo_arquivo = caminho_arquivo
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
            
        linhas = texto_completo.split('\n') 
        dados = [linha.split() for linha in linhas if linha.strip()] 
        df = pd.DataFrame(dados) 
        
        #exibindo as 5 primeiras linhas:
        #print(df.head(5))
        
        #exibindo todas as linhas mas só a primeira coluna:
        #print(f"#exibindo todas as linhas mas só a primeira coluna:\n{df}")
        

def Geracao_Pdf_Atendimen():
    global statusThread
    global df
    # ============================== Geracao_Pdf_Atendimen ==============================
    registrar_log('============================== Geracao_Pdf_Atendimen ==============================')

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

    # box de senha:
    box_senha = driver.find_element(By.XPATH, value='//*[@id="loginPassword"]')
    box_senha.send_keys('hsf@2024')
    registrar_log('box_senha')

    # botao de login:
    bt_login = driver.find_element(By.XPATH, value='//*[@id="loginForm"]/input[3]')
    bt_login.click()
    registrar_log('bt_login')

    driver.implicitly_wait(10)

    # click no atalho de utilitários:
    bt_utilitarios = driver.find_element(By.XPATH, value='//*[@id="app-view"]/tasy-corsisf1/div/w-mainlayout/div/div/w-launcher/div/ul/li[2]')
    bt_utilitarios.click()
    registrar_log('bt_utilitarios.click()')
    time.sleep(2)

    # click no atalho de bt_impressao_relatorios:
    bt_impressao_relatorios = driver.find_element(By.XPATH, value='//*[@id="app-view"]/tasy-corsisf1/div/w-mainlayout/div/div/w-launcher/div/div/div[2]/w-apps/div/div[1]/ul/li[3]/w-feature-app/a/img')
    bt_impressao_relatorios.click()
    registrar_log('bt_impressao_relatorios.click()')
    driver.implicitly_wait(5)
    time.sleep(5)

    # click no campo para procurar o relatório 1790:
    box_codigo_rel = driver.find_element(By.XPATH, value='//*[@id="detail_1_container"]/div[1]/div/div[2]/tasy-wtextbox/div/div/input')
    box_codigo_rel.send_keys('1790')
    registrar_log("box_codigo_rel.send_keys('1790')")
    driver.implicitly_wait(5)
    time.sleep(5)

    #Pressionar Item:
    pyautogui.press('enter')
    registrar_log("pyautogui.press('enter')")
    driver.implicitly_wait(5)
    time.sleep(5)
    
    # Click no botao visualizar:
    bt_visualizar_ = driver.find_element(By.XPATH, value='//*[@id="handlebar-455491"]')
    bt_visualizar_.click()
    registrar_log("bt_visualizar_.click()")
    driver.implicitly_wait(20)
    time.sleep(20)
    
    #click apos o download
    pyautogui.click(1810,165)
    registrar_log("click apos o download\npyautogui.click(1810,165)")
    driver.implicitly_wait(10)
    time.sleep(10)
    
    #Pressionar Item:
    pyautogui.press('enter')
    registrar_log("Pressionar Item\npyautogui.press('enter')")
    time.sleep(5)
    
    #click no manter:
    pyautogui.click(1751,109)
    registrar_log("click no manter\npyautogui.click(1751,109)")
    driver.implicitly_wait(5)
    time.sleep(5)
       
    #print(f"pdf_para_csv():\n{pdf_para_csv()}")
    
    #TODO: pdf_para_csv()
    #df = pdf_para_csv()
    
    #registrar_log(f"\nDF:\n{df}")
    
    # FIM:
    statusThread = False
    registrar_log(f"global statusThread: {statusThread}")
    
    # pausa dramática:
    driver.implicitly_wait(2)
    time.sleep(2)
    driver.quit()
    
    registrar_log("=========== FIM ========")

def Geracao_Pdf_Prescricao():
    global statusThread
    global df
    global df_filtrado
    # ============================== Geracao_Pdf_Prescricao ==============================
    registrar_log('============================== Geracao_Pdf_Prescricao ==============================')
    
    df_filtrado = df.iloc[:, 0]
    registrar_log(f"df_filtrado: {df_filtrado}")
    """     
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
    driver.implicitly_wait(1.5)
    time.sleep(2)

    # box de senha:
    box_senha = driver.find_element(By.XPATH, value='//*[@id="loginPassword"]')
    box_senha.send_keys('hsf@2024')
    registrar_log('box_senha')
    driver.implicitly_wait(1.5)
    time.sleep(2)

    # botao de login:
    bt_login = driver.find_element(By.XPATH, value='//*[@id="loginForm"]/input[3]')
    bt_login.click()
    registrar_log('bt_login')
    driver.implicitly_wait(1.5)
    time.sleep(10)
    
    #TODO: aqui vai ser feita a sequencia de repetições para emitir os pdfs
    
    # Percorrendo cada linha e coluna e exibindo os dados no console
    print("\n***********************Exibindo dados linha por linha:")
    for linha in df_filtrado.iloc[:, 0]:
        registrar_log(f"Repeticao:\nNR_ATENDIMENTO: {linha}")
        
        # escrever CPOE
        pyautogui.write('CPOE')
        registrar_log('CPOE')
        time.sleep(5)
    
        #dar enter:
        pyautogui.press('enter')
        registrar_log('enter')
        time.sleep(5)
    
        #clicar no icone do CPOE:
        bt_CPOE = driver.find_element(By.XPATH, value='//*[@id="app-view"]/tasy-corsisf1/div/w-mainlayout/div/div/w-launcher/div/div/div[1]/w-apps/div/div[1]/ul/li/w-feature-app/a/img')
        bt_CPOE.click()
        registrar_log('clicar no icone do CPOE:')
        driver.implicitly_wait(5)
        time.sleep(5)
    
        #nr_atendimento
        pyautogui.write(linha)
        registrar_log(f'nr_atendimento: {linha}')
        driver.implicitly_wait(5)
        time.sleep(5)
        
        #enter
        pyautogui.press('enter')
        registrar_log('enter')
        driver.implicitly_wait(5)
        time.sleep(5)
        
        #enter
        pyautogui.press('enter')
        registrar_log('enter')
        driver.implicitly_wait(5)
        time.sleep(5)
        
        #botao visualizar
        bt_cpoe_relatorios = driver.find_element(By.XPATH, value='//*[@id="handlebar-40"]')
        bt_cpoe_relatorios.click()
        driver.implicitly_wait(5)
        time.sleep(5)
        
        #TODO: ajustar por que dependendo da tela ele não irá clicar:
        
        #click no visualizar:
        pyautogui.click(1456, 380)
        registrar_log("click no visualizar\npyautogui.click(1456, 380)")
        driver.implicitly_wait(15)
        #TODO: aumentar esse tempo para 45
        time.sleep(20)
        
        #clicar para baixar o pdf gerado
        pyautogui.click(1813,167)
        registrar_log("clicar para baixar o pdf gerado\npyautogui.click(1813,167)")
        driver.implicitly_wait(5)
        #TODO: aumentar esse tempo para 45
        time.sleep(5)
        
        #enter
        pyautogui.press('enter')
        registrar_log('enter')
        driver.implicitly_wait(5)
        time.sleep(5)
        
        #clicar para manter
        pyautogui.click(1750,108)
        registrar_log("clicar para manter\npyautogui.click(1750,108)")
        driver.implicitly_wait(5)
        #TODO: aumentar esse tempo para 45
        time.sleep(5)
        
        
        
        #TODO: renomear o pdf gerado para o nr_atendimento e hora gerado
        
        #TODO: movimentar pdf gerado para a pasta desejada
        
        
        
        
        #FIM
        registrar_log('driver.implicitly_wait(10)')
        driver.implicitly_wait(10)
        #TODO: retirar a pausa abaixo:
        time.sleep(10)
    
    
    registrar_log('driver.implicitly_wait(10)')
    driver.implicitly_wait(10)

    #TODO: fazer rotina para puxar os numero de atendimento
    
    
    
    # FIM:
    statusThread = False
    registrar_log(f"============================== FIM:!\nglobal statusThread: {statusThread}")
    
    # pausa dramática:
    driver.implicitly_wait(2)
    time.sleep(20)
    driver.quit()
    
    
    """
    
    
    
def interface_grafica():
    registrar_log("interface_grafica()")

    def iniciar():
        global statusThread
        global df_filtrado
        global df
        registrar_log("def iniciar()")
        registrar_log("Botao Iniciar clicado!")

        #validacao da variavel global:
        registrar_log(f"global statusThread: {statusThread}")

        if statusThread:
            registrar_log(f"Thread já foi iniciada, statusThread: \n{statusThread}")
            messagebox.showinfo("Tarefa já incializada!")

        else:
            statusThread = True
            registrar_log("============================== execuçao ========================")
            registrar_log(f"Tarefa inicializada!\nstatusThread:{statusThread}")
            
            #============================== execuçao ========================

            #TODO: inserir a execucao do login do tasy em uma thread:
            
            #delete_all_files_in_directory(pasta_downloads)
            
            #Geracao_Pdf_Atendimen()
            
            pdf_para_csv()
            Geracao_Pdf_Prescricao()
            
            
            
                

    def fechar():
        registrar_log("def fechar()")
        # Exiba uma caixa de diálogo de confirmação
        resultado = messagebox.askyesno("Confirmação", "Tem certeza de que deseja fechar o aplicativo?")
        if resultado:
            # Feche o aplicativo
            registrar_log("janela.destroy()")
            janela.destroy()

    #INTERFACE GRAFICA:
    janela = tk.Tk()
    janela.maxsize(600,400)
    janela.geometry('600x400')
    janela.title("RPA PRESCRICOES POR SETOR")

    bt_Iniciar = tk.Button(janela, width=18, text="Iniciar",command=lambda: [
        #TODO: TESTAR ETAPAS DO SISTEMA ABAIXO
        iniciar()
    ])
    bt_Iniciar.place(x=80 , y=215)

    bt_fechar = tk.Button(janela, width=18, text="Fechar", command=lambda: [fechar()])
    bt_fechar.place(x=350 , y=215)

    janela.mainloop()



if __name__ == "__main__":
    try:
        registrar_log("============================== inicio ========================")
        
        #deletando todos os arquivos da pasta download
        pasta_downloads = os.path.join(os.path.expanduser("~"), "Downloads")
                
        #iniciando interface grafica
        interface_grafica()

    except Exception as erro:
        registrar_log(f"================================ Error: \n{erro}")