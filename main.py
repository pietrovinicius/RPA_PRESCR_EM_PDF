import tkinter as tk
import os
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By

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
    janela = tk.Tk()
    janela.maxsize(600,400)
    janela.geometry('600x400')
    janela.title("RPA PRESCRICOES POR SETOR")

    

    janela.mainloop()

if __name__ == "__main__":
    try:
        print("\n============================== inicio ========================")
        registrar_log("============================== inicio ========================")
        interface_grafica()

    except Exception as erro:
        print(f"================================ Error: \n{erro}")
        registrar_log(f"================================ Error: \n{erro}")