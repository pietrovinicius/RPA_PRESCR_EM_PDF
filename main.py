import tkinter as tk
import os
import datetime
import threading
from tkinter import messagebox

from selenium import webdriver
from selenium.webdriver.common.by import By

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

            #\n============================== execuçao ========================

            driver = webdriver.Chrome()

            driver.get("http://aplicacao.hsf.local:7070/#/login")
            registrar_log('driver.get("http://aplicacao.hsf.local:7070/#/login")')
            print('driver.get("http://aplicacao.hsf.local:7070/#/login")')
            title = driver.title
            driver.implicitly_wait(1.5)

    def fechar():
        registrar_log("def fechar()")
        print("Botão fechar clicado!")
        janela.destroy()

    janela = tk.Tk()
    janela.maxsize(600,400)
    janela.geometry('600x400')
    janela.title("RPA PRESCRICOES POR SETOR")

    bt_Iniciar = tk.Button(janela, text="Iniciar",command=lambda: [iniciar()])
    bt_Iniciar.pack(fill="both", expand=True , padx=100 , pady=5 )

    bt_fechar = tk.Button(janela, text="Fechar", command=lambda: [fechar()])
    bt_fechar.pack(fill="both", expand=True , padx=100 , pady=5 )

    janela.mainloop()

if __name__ == "__main__":
    try:
        print("\n============================== inicio ========================")
        registrar_log("============================== inicio ========================")
        interface_grafica()

    except Exception as erro:
        print(f"================================ Error: \n{erro}")
        registrar_log(f"================================ Error: \n{erro}")