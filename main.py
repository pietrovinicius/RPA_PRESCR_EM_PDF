"""
24/10/2024
@PLima

Automação PDID - Extrai em pdf todas as prescrições dos pacientes Internados
"""

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
diretorio_atual_prescricoes = ""


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
    #Função para registrar um texto em um arquivo de log.
    diretorio_atual = os.getcwd()
    caminho_arquivo = os.path.join(diretorio_atual, 'log.txt')
    print(f"{agora()} - {texto}\n")

    # Abre o arquivo em modo de append (adiciona texto ao final)
    with open(caminho_arquivo, 'a') as arquivo:
        arquivo.write(f"{agora()} - {texto}\n")
    
def delete_all_files_in_directory():
    #acessando pasta download:
    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
    registrar_log(f'Caminho da pasta download: {downloads_path}')
    
    registrar_log(f"delete_all_files_in_directory({downloads_path})")
    files = glob.glob(os.path.join(downloads_path, '*'))
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
    
def pdf_para_df():
    global df_filtrado
    global df
    global statusThread
    texto_completo = ""
    
    registrar_log("******def pdf_para_df():")
    
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
    
    renomeado_arquivo = os.path.join(diretorio_atual, 'Atendimentos.pdf')
    
    registrar_log(f"*****caminho_arquivo: {renomeado_arquivo}")
    
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
            
        linhas = texto_completo.split('\n') 
        dados = [linha.split() for linha in linhas if linha.strip()] 
        df = pd.DataFrame(dados)
        #exibindo as 5 primeiras linhas:
        #print(df.head(5))
        
        #exibindo todas as linhas mas só a primeira coluna:
        #print(f"#exibindo todas as linhas mas só a primeira coluna:\n{df}")
    return df
        
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
    time.sleep(5)
    
    #1107,702    
    pyautogui.click(1107,702  )
    registrar_log("click objeto inválido\npyautogui.click(1107,702)")
    time.sleep(2)

    # click no atalho de utilitários:
    bt_utilitarios = driver.find_element(By.XPATH, value='//*[@id="app-view"]/tasy-corsisf1/div/w-mainlayout/div/div/w-launcher/div/ul/li[2]')
    bt_utilitarios.click()
    registrar_log('bt_utilitarios.click()')
    time.sleep(2)

    # click no atalho de bt_impressao_relatorios:
    bt_impressao_relatorios = driver.find_element(By.XPATH, value='//*[@id="app-view"]/tasy-corsisf1/div/w-mainlayout/div/div/w-launcher/div/div/div[2]/w-apps/div/div[1]/ul/li[3]/w-feature-app/a/img')
    bt_impressao_relatorios.click()
    registrar_log('bt_impressao_relatorios.click()')
    driver.implicitly_wait(1.5)
    time.sleep(2)

    # click no campo para procurar o relatório 1790:
    box_codigo_rel = driver.find_element(By.XPATH, value='//*[@id="detail_1_container"]/div[1]/div/div[2]/tasy-wtextbox/div/div/input')
    box_codigo_rel.send_keys('1790')
    registrar_log("box_codigo_rel.send_keys('1790')")
    driver.implicitly_wait(1.5)
    time.sleep(2)

    #Pressionar Item:
    pyautogui.press('enter')
    registrar_log("pyautogui.press('enter')")
    driver.implicitly_wait(1.5)
    time.sleep(2)
    
    # Click no botao visualizar:
    bt_visualizar_ = driver.find_element(By.XPATH, value='//*[@id="handlebar-455491"]')
    bt_visualizar_.click()
    registrar_log("bt_visualizar_.click()")
    driver.implicitly_wait(5)
    time.sleep(5)
    
    #click apos o download
    #pyautogui.click(1810,165)
    #pyautogui.click(1781,149)
    registrar_log("8x tab - inicio")
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.press('tab')
    registrar_log("8x tab - fim")
    driver.implicitly_wait(1)
    time.sleep(1)
    
    #Pressionar Item:
    pyautogui.press('enter')
    registrar_log("Pressionar Item\npyautogui.press('enter')")
    time.sleep(1)
    
    #Pressionar Item:
    pyautogui.press('enter')
    registrar_log("Pressionar Item\npyautogui.press('enter')")
    time.sleep(1)
    
    registrar_log("8x tab - inicio")
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.press('tab')
    registrar_log("8x tab - fim")
    driver.implicitly_wait(1)
    time.sleep(1)
    
    #Pressionar Item:
    pyautogui.press('enter')
    registrar_log("Pressionar Item\npyautogui.press('enter')")
    time.sleep(1)
    
    registrar_log("5x tab - inicio")
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.press('tab')
    registrar_log("5x tab - fim")
    driver.implicitly_wait(1)
    time.sleep(1)
    
    #Pressionar Item:
    pyautogui.press('enter')
    registrar_log("Pressionar Item\npyautogui.press('enter')")
    time.sleep(1)
    
    # FIM:
    statusThread = False
    registrar_log(f"global statusThread: {statusThread}")
    
    # pausa dramática:
    driver.implicitly_wait(2)
    time.sleep(2)
    driver.quit()
    
    registrar_log("=========== Geracao_Pdf_Atendimen fim ========")

def Geracao_Pdf_Prescricao():
    global statusThread
    global df
    global df_filtrado
    global diretorio_atual_prescricoes
    # ============================== Geracao_Pdf_Prescricao ==============================
    registrar_log('============================== Geracao_Pdf_Prescricao ==============================')
    
    df_filtrado = df.iloc[:, 0]
    #print(f"df_filtrado: {df_filtrado}")
    
    contador = 0
    
    #=================================== REPETICAO #=================================== 
    #Percorrendo cada linha e coluna e exibindo os dados no console
    print("\n***********************Exibindo dados linha por linha:")
    
    
    try:
        for linha in df_filtrado:
            try:
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
                time.sleep(5)
                
                #1107,702    
                pyautogui.click(1107,702  )
                registrar_log("click objeto inválido\npyautogui.click(1107,702)")
                time.sleep(2)
                
                #TODO: aqui vai ser feita a sequencia de repetições para emitir os pdfs
                registrar_log("for linha in df_filtrado.iloc[:, 0]")
                registrar_log(f"Repeticao:\nNR_ATENDIMENTO: {linha}")
                
                #clicar no icone do CPOE:
                bt_CPOE = driver.find_element(By.XPATH, value='//*[@id="app-view"]/tasy-corsisf1/div/w-mainlayout/div/div/w-launcher/div/div/div[1]/w-apps/div/div[1]/ul/li[2]/w-feature-app/a/img')
                bt_CPOE.click()
                registrar_log('clicar no icone do CPOE:')
                driver.implicitly_wait(20)
                time.sleep(20)
                                
                #nr_atendimento
                driver.implicitly_wait(1.5)
                pyautogui.write(linha)
                registrar_log(f'nr_atendimento: {linha}')
                driver.implicitly_wait(1.5)
                time.sleep(2)

                #enter
                pyautogui.press('enter')
                registrar_log('1 - enter')
                driver.implicitly_wait(1.5)
                time.sleep(2)

                #enter
                pyautogui.press('enter')
                registrar_log('2 - enter')
                driver.implicitly_wait(10)
                time.sleep(10)

                #click atendimento fechado
                pyautogui.click(1100,709)
                registrar_log("click atendimento fechado")
                driver.implicitly_wait(2)
                time.sleep(2)

                #botao visualizar
                bt_cpoe_relatorios = driver.find_element(By.XPATH, value='//*[@id="handlebar-40"]')
                bt_cpoe_relatorios.click()
                registrar_log("bt_cpoe_relatorios.click()")
                driver.implicitly_wait(1)
                time.sleep(1)
                
                #botao visualizar
                bt_cpoe_visualizar = driver.find_element(By.XPATH, value='//*[@id="popupViewPort"]/li[5]/div[3]')
                bt_cpoe_visualizar.click()
                registrar_log("bt_cpoe_visualizar")
                driver.implicitly_wait(10)
                time.sleep(10)
                
                #tab apos o download
                registrar_log("8x tab - inicio")
                pyautogui.press('tab')
                pyautogui.press('tab')
                pyautogui.press('tab')
                pyautogui.press('tab')
                pyautogui.press('tab')
                pyautogui.press('tab')
                pyautogui.press('tab')
                pyautogui.press('tab')
                registrar_log("8x tab - fim")
                driver.implicitly_wait(1)
                time.sleep(1)
                
                #Pressionar Item:
                pyautogui.press('enter')
                registrar_log("Pressionar Item\npyautogui.press('enter') 1")
                time.sleep(1)
                
                #Pressionar Item:
                pyautogui.press('enter')
                registrar_log("Pressionar Item\npyautogui.press('enter') 2")
                time.sleep(1)
                
                registrar_log("8x tab - inicio")
                pyautogui.press('tab')
                pyautogui.press('tab')
                pyautogui.press('tab')
                pyautogui.press('tab')
                pyautogui.press('tab')
                pyautogui.press('tab')
                pyautogui.press('tab')
                pyautogui.press('tab')
                registrar_log("8x tab - fim")
                driver.implicitly_wait(1)
                time.sleep(1)
                
                #Pressionar Item:
                pyautogui.press('enter')
                registrar_log("Pressionar Item\npyautogui.press('enter') 1")
                time.sleep(1)
                
                registrar_log("5x tab - inicio")
                pyautogui.press('tab')
                pyautogui.press('tab')
                pyautogui.press('tab')
                pyautogui.press('tab')
                pyautogui.press('tab')
                registrar_log("5x tab - fim")
                driver.implicitly_wait(1)
                time.sleep(1)
                
                #Pressionar Item:
                pyautogui.press('enter')
                registrar_log("Pressionar Item\npyautogui.press('enter') 1")
                time.sleep(1)
            
                #acessando pasta download:
                downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
                registrar_log(f'Caminho da pasta download: {downloads_path}')
                time.sleep(1)
                
                #verificando arquivos da pasta download
                files = [f for f in os.listdir(downloads_path) if f.endswith('.pdf')]
                registrar_log(f"Arquivos:\n{files}")
                time.sleep(1)
                #ultimo arquivo
                ultimo_arquivo = os.path.join(downloads_path, files[0])
                registrar_log(f"\n*****Ultimo arquivo antes de renomear: {ultimo_arquivo}")

                time.sleep(1)
                
                # Caminho da pasta Prescricoes
                #data_hora = agora_limpo()
                pasta_prescricoes = "Prescricoes"
                registrar_log(f"pasta_prescricoes: {pasta_prescricoes}")
                time.sleep(1)
                
                pasta_data = os.path.join(pasta_prescricoes, agora_limpo())
                registrar_log(f"pasta_data: {pasta_data}")
                time.sleep(1)

                # Cria a pasta da data se não existir
                os.makedirs(pasta_data, exist_ok=True)
                registrar_log(f"***********os.makedirs: {pasta_data}")
                time.sleep(1)

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
                    registrar_log(f"Arquivo {ultimo_arquivo} renomeado e movido com sucesso.")
                except shutil.Error as e:
                    registrar_log(f"Erro ao mover o arquivo: {e}")
                    
                time.sleep(2)
                #FIM
                contador += 1
                registrar_log(f'\ncontador = {contador}\nAtendimento:{linha}\n\n********************FIM********************\n')
                
                # pausa dramática:
                driver.implicitly_wait(2)
                time.sleep(2)
                driver.quit()
                
            except Exception as erro:
                registrar_log(f"=========== except do try de dento do for linha in df_filtrado::\ncontador: {contador} \n{erro}")
    except Exception as erro:
        #TODO: ao terminar extoura um exception e cai nesse bloco
        registrar_log(f"=========== except: for linha in df_filtrado::\ncontador: {contador} \n{erro}")
    
    #TODO: Apos o erro ele segue com a execucao e precisa agora rodar novamente na hora pre determinda
    registrar_log('\nFinal do for linha\ndriver.implicitly_wait(10)')
    #driver.implicitly_wait(10)

    # FIM:
    statusThread = False
    registrar_log(f"============================== Geracao_Pdf_Prescricao FIM!\nglobal statusThread: {statusThread}")
    
    
def interface_grafica():
    registrar_log("interface_grafica()")
    
    def ao_fechar():
        resultado = messagebox.askyesno("Confirmação", "Tem certeza de que deseja fechar o aplicativo?")
        if resultado:
            # Feche o aplicativo
            janela.destroy()
        """Função chamada quando o usuário clica no botão 'X' para fechar a janela."""
        registrar_log("O aplicativo foi fechado no botão X\n")
        
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
            registrar_log("============================== execucao ========================")
            registrar_log(f"Tarefa inicializada!\nstatusThread:{statusThread}")
            
            #============================== execucao ========================
            #TODO: inserir a execucao do login do tasy em um process
            delete_all_files_in_directory()
            Geracao_Pdf_Atendimen()
            print(pdf_para_df())
            Geracao_Pdf_Prescricao()
    
    def fechar():
        registrar_log(f"\n\n{agora()}def fechar()- janela.destroy()")
        # Exiba uma caixa de diálogo de confirmação
        #resultado = messagebox.askyesno("Confirmação", "Tem certeza de que deseja fechar o aplicativo?")
        #if resultado:
        #    # Feche o aplicativo
        #    registrar_log("janela.destroy()")
        #    janela.destroy()
        janela.destroy()

    #INTERFACE GRAFICA:
    janela = tk.Tk()
    janela.maxsize(600,400)
    janela.geometry('600x400')
    janela.title("RPA PRESCRICOES POR SETOR")
    
    # Associa a função ao_fechar ao evento de fechamento da janela
    janela.protocol("WM_DELETE_WINDOW", ao_fechar)

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
        registrar_log(f"\n\n\n\n{agora()}\n============================== INICIO ========================\n")
        
        #deletando todos os arquivos da pasta download
        pasta_downloads = os.path.join(os.path.expanduser("~"), "Downloads")
                
        #iniciando interface grafica
        interface_grafica()

    except Exception as erro:
        registrar_log(f'================================ if __name__ == "__main__"\nException Error: \n{erro}')