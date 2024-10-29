import tkinter as tk
import os
import datetime
import threading
from tkinter import messagebox

from selenium import webdriver
from selenium.webdriver.common.by import By

import time

import pyautogui

#inicialização de variaveis globais:
statusThread = False

def agora_limpo():
    agora_limpo = datetime.datetime.now()
    agora_limpo = agora_limpo.strftime("%d/%m/%Y %H:%M:%S")
    #agora_limpo = agora_limpo.replace(":", "_").replace("/", "_")
    return str(agora_limpo)

def registrar_log(texto):
  #Função para registrar um texto em um arquivo de log.
  diretorio_atual = os.getcwd()
  caminho_arquivo = os.path.join(diretorio_atual, 'log.txt')

  # Abre o arquivo em modo de append (adiciona texto ao final)
  with open(caminho_arquivo, 'a') as arquivo:
    arquivo.write(f"{agora_limpo()} - {texto}\n")


def login_tasy():
    # ============================== login no sistema ==============================
    registrar_log('============================== login no sistema ==============================')
    print('============================== login no sistema ==============================')

    driver = webdriver.Chrome()

    driver.get("http://aplicacao.hsf.local:7070/#/login")
    registrar_log('driver.get("http://aplicacao.hsf.local:7070/#/login")')
    print('driver.get("http://aplicacao.hsf.local:7070/#/login")')
    title = driver.title

    driver.implicitly_wait(1.5)

    # box de usuario:
    box_usuario = driver.find_element(By.XPATH, value='//*[@id="loginUsername"]')
    box_usuario.send_keys('pvplima')
    registrar_log('box_usuario')
    print("box_usuario.send_keys('pvplima')")

    box_senha = driver.find_element(By.XPATH, value='//*[@id="loginPassword"]')
    box_senha.send_keys('hsf@2024')
    registrar_log('box_senha')
    print("box_senha.send_keys(********)")

    bt_login = driver.find_element(By.XPATH, value='//*[@id="loginForm"]/input[3]')
    bt_login.click()
    registrar_log('bt_login')
    print("bt_login.click()")

    driver.implicitly_wait(10)
    time.sleep(12)
    #digitar a palavra PEP
    print('time.sleep(12)')

    print("pyautogui.write('PEP')")
    pyautogui.write('PEP')
    time.sleep(8)

    print("bt_procura.send_keys('PEP')")
    #bt_procura = driver.find_element(By.XPATH, value='//*[@id="app-view"]/tasy-corsisf1/div/w-mainlayout/div/div/w-launcher/div/input')
    #bt_procura.send_keys('PEP')

    bt_PEP = driver.find_element(By.XPATH, value='//*[@id="app-view"]/tasy-corsisf1/div/w-mainlayout/div/div/w-launcher/div/div/div[1]/w-apps/div/div[1]/ul/li[4]/w-feature-app/a/img')
    bt_PEP.click()

    driver.implicitly_wait(10)

    # pausa dramática:
    time.sleep(8)


def interface_grafica():
    registrar_log("interface_grafica()")

    def iniciar():
        global statusThread
        registrar_log("def iniciar()")
        print("Botão Iniciar clicado!")
        registrar_log("Botão Iniciar clicado!")

        #validacao da variavel global:
        print(f"global statusThread: {statusThread}")

        if statusThread:
            registrar_log(f"Thread já foi iniciada, statusThread: \n{statusThread}")
            print(f"Thread já foi iniciada, statusThread: \n{statusThread}")

            messagebox.showinfo("Tarefa já incializada!")

        else:
            statusThread = True
            registrar_log("Tarefa inicializada!")
            print("Tarefa inicializada!")

            #============================== execuçao ========================

            login_tasy()





    def fechar():
        registrar_log("def fechar()")
        print("Botao fechar clicado!")
        janela.destroy()

    janela = tk.Tk()
    janela.maxsize(600,400)
    janela.geometry('600x400')
    janela.title("RPA PRESCRICOES POR SETOR")

    bt_Iniciar = tk.Button(janela, width=18, text="Iniciar",command=lambda: [iniciar()])
    bt_Iniciar.place(x=80 , y=215)

    bt_fechar = tk.Button(janela, width=18, text="Fechar", command=lambda: [fechar()])
    bt_fechar.place(x=350 , y=215)

    janela.mainloop()

if __name__ == "__main__":
    try:
        print("\n============================== inicio ========================")
        registrar_log("============================== inicio ========================")
        interface_grafica()

    except Exception as erro:
        print(f"================================ Error: \n{erro}")
        registrar_log(f"================================ Error: \n{erro}")