import tkinter as tk

def interface_grafica():
    janela = tk.Tk()
    janela.maxsize(600,400)
    janela.geometry('600x400')
    janela.title("RPA PRESCRICOES POR SETOR")

    janela.mainloop()

if __name__ == "__main__":
    print("============================== inicio ========================")

    print("Criação de janela")

    interface_grafica()