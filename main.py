import tkinter as tk

from selenium import webdriver
from selenium.webdriver.common.by import By

def interface_grafica():
    janela = tk.Tk()
    janela.maxsize(600,400)
    janela.geometry('600x400')
    janela.title("RPA PRESCRICOES POR SETOR")

    janela.mainloop()

if __name__ == "__main__":
    try:
        print("\n============================== inicio ========================")
        print("Criação de janela")
        interface_grafica()

    except Exception as erro:
        print(f"================================ Error: \n{erro}")