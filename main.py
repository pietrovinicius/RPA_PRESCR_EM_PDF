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

import os
import glob


#inicialização de variaveis globais:
statusThread = False
df = ""

def agora_limpo():
    agora_limpo = datetime.datetime.now()
    agora_limpo = agora_limpo.strftime("%d/%m/%Y %H:%M:%S")
    #agora_limpo = agora_limpo.replace(":", "_").replace("/", "_")
    return str(agora_limpo)

def registrar_log(texto):
  #Função para registrar um texto em um arquivo de log.
  diretorio_atual = os.getcwd()
  caminho_arquivo = os.path.join(diretorio_atual, 'log.txt')
  print(texto)

  # Abre o arquivo em modo de append (adiciona texto ao final)
  with open(caminho_arquivo, 'a') as arquivo:
    arquivo.write(f"{agora_limpo()} - {texto}\n")
    
def delete_all_files_in_directory(directory):
    files = glob.glob(os.path.join(directory, '*'))
    for f in files:
        try:
            os.remove(f)
            print(f"Arquivo {f} removido com sucesso.")
        except Exception as e:
            print(f"Não foi possível remover o arquivo {f}. Erro: {e}")

def Execucao():
    global statusThread
    # ============================== login no sistema ==============================
    registrar_log('============================== login no sistema ==============================')

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

    #TODO: fazer rotina para puxar os numero de atendimento

    # click no atalho de utilitários:
    bt_utilitarios = driver.find_element(By.XPATH, value='//*[@id="app-view"]/tasy-corsisf1/div/w-mainlayout/div/div/w-launcher/div/ul/li[2]')
    bt_utilitarios.click()
    registrar_log('bt_utilitarios.click()')
    time.sleep(2)

    # click no atalho de bt_impressao_relatorios:
    bt_impressao_relatorios = driver.find_element(By.XPATH, value='//*[@id="app-view"]/tasy-corsisf1/div/w-mainlayout/div/div/w-launcher/div/div/div[2]/w-apps/div/div[1]/ul/li[3]/w-feature-app/a/img')
    bt_impressao_relatorios.click()
    registrar_log('bt_impressao_relatorios.click()')
    time.sleep(2)

    # click no campo para procurar o relatório 1789:
    box_codigo_rel = driver.find_element(By.XPATH, value='//*[@id="detail_1_container"]/div[1]/div/div[2]/tasy-wtextbox/div/div/input')
    box_codigo_rel.send_keys('1790')
    registrar_log("box_codigo_rel.send_keys('1790')")
    time.sleep(2)

    #Pressionar Item:
    pyautogui.press('enter')
    registrar_log("pyautogui.press('enter')")
    time.sleep(2)
    
    
    # Click no botao visualizar:
    bt_visualizar_ = driver.find_element(By.XPATH, value='//*[@id="handlebar-455491"]')
    bt_visualizar_.click()
    registrar_log("bt_visualizar_.click()")
    time.sleep(12)
    
    #click apos o download
    pyautogui.click(1810,165)
    registrar_log("pyautogui.click(1811,167)")
    
    #click no manter:
    registrar_log("click no manter")
    time.sleep(10)
    
    
    #Pressionar Item:
    pyautogui.press('enter')
    registrar_log("pyautogui.press('enter')")
    time.sleep(4)
    
    pyautogui.click(1751,109)
    registrar_log("pyautogui.click(1749,145)")
    
    
    
    """
    # click no botao exportar xlsx:
    bt_exportar_xls = driver.find_element(By.XPATH, value='//*[@id="handlebar-956041"]')
    bt_exportar_xls.click()
    registrar_log('bt_exportar_xls.click()')
    time.sleep(2)
    
    # click no botao de exportar xls:
    bt_continuar_export_xls = driver.find_element(By.XPATH, value='//*[@id="ngdialog1"]/div[2]/div[1]/div[2]/div[2]/tasy-wdlgpanel-button/button')
    bt_continuar_export_xls.click()
    registrar_log("bt_continuar_export_xls.click()")

    #driver.implicitly_wait(20)
    #registrar_log("driver.implicitly_wait(20)")
    time.sleep(20)
    registrar_log("time.sleep(10)")
    
    #click apos o download
    pyautogui.click(1824,64)
    registrar_log("pyautogui.click(1824,64)")
    
    #click no manter:
    registrar_log("click no manter")
    time.sleep(4)
    pyautogui.click(1749,145)
    registrar_log("pyautogui.click(1749,145)")
    time.sleep(4)
    """
    
    
    #TODO: funcao para pegar planilha gerada e montar o data frame:
    
    #caminho_pasta_download = "C:\Users\pvplima.C19NOT76\Downloads"
    
    
    
    
    # TODO: sequencia para inicio de abertura do CPOE para geracao dos pdfs
    """
    #digitar a palavra PEP
    time.sleep(12)
    pyautogui.write('PEP')
    time.sleep(8)

    #bt_procura = driver.find_element(By.XPATH, value='//*[@id="app-view"]/tasy-corsisf1/div/w-mainlayout/div/div/w-launcher/div/input')
    #bt_procura.send_keys('PEP')

    
    # click no atalho do PEP no tasy:
    bt_PEP = driver.find_element(By.XPATH, value='//*[@id="app-view"]/tasy-corsisf1/div/w-mainlayout/div/div/w-lPacientesauncher/div/div/div[1]/w-apps/div/div[1]/ul/li[4]/w-feature-app/a/img')
    bt_PEP.click()
    """
    
    
    

    time.sleep(20)


    # FIM:
    statusThread = False
    registrar_log(f"global statusThread: {statusThread}")
    registrar_log("=========== FIM ========")

    # pausa dramática:
    driver.implicitly_wait(60)
    time.sleep(8)
    driver.quit()

def interface_grafica():
    registrar_log("interface_grafica()")

    def iniciar():
        global statusThread
        registrar_log("def iniciar()")
        registrar_log("Botao Iniciar clicado!")

        #validacao da variavel global:
        registrar_log(f"global statusThread: {statusThread}")

        if statusThread:
            registrar_log(f"Thread já foi iniciada, statusThread: \n{statusThread}")
            messagebox.showinfo("Tarefa já incializada!")

        else:
            statusThread = True
            registrar_log("Tarefa inicializada!")

            #============================== execuçao ========================

            #TODO: inserir a execucao do login do tasy em uma thread:
            Execucao()

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
        interface_grafica()

    except Exception as erro:
        registrar_log(f"================================ Error: \n{erro}")