"""
24/10/2024
@PLima

Automação PDD - Extrai em pdf todas as prescrições dos pacientes Internados
"""
import tkinter as tk
import os
import datetime
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pyautogui
import os
import pandas as pd
import os
import glob
import shutil
import schedule
import oracledb
import sys
import configparser
import threading

#inicialização de variaveis globais:
diretorio_atual = ""
statusMultiprocessing = False
df = ""

df_filtrado = ""
diretorio_atual_prescricoes = ""

lista_nr_atendimento = []

lb_contador = 0

#variáveis de controle:
tarefa_agendada_iniciada = False
tarefa_executada = False
tarefa_executada_erro = False

# Flag global para controle da thread
thread_ativa = True 
threadExecutar = None # adicionei

# Constante para tempo de espera:
TEMPO_ESPERA = 10

def agora_limpo():
    agora_limpo = datetime.datetime.now()
    agora_limpo = agora_limpo.strftime("%Y/%m/%d")    
    agora_limpo = agora_limpo.replace(":", "_").replace("/", "_")
    return str(agora_limpo)

def agora():
    agora = datetime.datetime.now()
    agora = agora.strftime("%Y-%m-%d %H:%M:%S")
    return str(agora)

def obter_configuracao(secao, chave):
    """    Lê uma configuração de um arquivo config.ini.    """
    global diretorio_atual
    config = configparser.ConfigParser()
    caminho_arquivo_config = os.path.join(diretorio_atual, 'config.ini')
    
    try:
        config.read(caminho_arquivo_config)
        return config[secao][chave]
    except KeyError:
        registrar_log(f"Erro: Chave '{chave}' não encontrada na seção '{secao}' em '{caminho_arquivo_config}'.")
        return None

def obter_credenciais_login():
    """Lê as credenciais de login do arquivo config.ini.Retorna o usuário e a senha como uma tupla (usuario, senha).    """
    registrar_log('Obter_credenciais_login() - lendo do config.ini')
    # Certifique-se de que 'obter_configuracao' está definida e funcional antes desta chamada.
    # Ela deve ser capaz de ler a seção 'CREDENTIALS' e as chaves 'username' e 'password'.
    usuario = obter_configuracao('CREDENTIALS', 'username')
    senha = obter_configuracao('CREDENTIALS', 'password')
    
    if usuario is None or senha is None:
        registrar_log("Erro: Credenciais não encontradas no config.ini. Verifique a seção [CREDENTIALS].")
        return None, None
    
    return usuario, senha

def registrar_log(texto):
    global diretorio_atual
    #Função para registrar um texto em um arquivo de log.
    diretorio_atual = os.getcwd()
    caminho_arquivo = os.path.join(diretorio_atual, 'log.txt')
    print(f"{agora()} - {texto}\n")

    # Abre o arquivo em modo de append (adiciona texto ao final)
    with open(caminho_arquivo, 'a') as arquivo:
        arquivo.write(f"{agora()} - {texto}\n")
    
def registrar_log_cronometro(texto):
    global diretorio_atual
    #Função para registrar um texto em um arquivo de log.
    diretorio_atual = os.getcwd()
    caminho_arquivo = os.path.join(diretorio_atual, 'log_cronometro.txt')
    # Abre o arquivo em modo de append (adiciona texto ao final)
    with open(caminho_arquivo, 'w') as arquivo:
        print(f"{agora()} - {texto}\n")
        arquivo.write(f"{agora()} - {texto}\n")

def registrar_log_atend_erros(texto):
    global diretorio_atual
    #Função para registrar um texto em um arquivo de log.
    diretorio_atual = os.getcwd()
    caminho_arquivo = os.path.join(diretorio_atual, 'log_atend_erros.txt')
    # Abre o arquivo em modo de append (adiciona texto ao final)
    with open(caminho_arquivo, 'a') as arquivo:
        print(f"{texto}")
        arquivo.write(f"{agora()} - {texto}\n")

def registrar_log_contador(texto):
    global diretorio_atual
    #Função para registrar um texto em um arquivo de log.
    diretorio_atual = os.getcwd()
    caminho_arquivo = os.path.join(diretorio_atual, 'log_contador.txt')
    # Abre o arquivo em modo de append (adiciona texto ao final)
    with open(caminho_arquivo, 'w') as arquivo:
        print(f"{texto}")
        arquivo.write(texto)

def registrar_log_tarefa_executada(texto):
    global diretorio_atual
    #Função para registrar um texto em um arquivo de log.
    diretorio_atual = os.getcwd()
    caminho_arquivo = os.path.join(diretorio_atual, 'log_tarefa_executada.txt')
    # Abre o arquivo em modo de append (adiciona texto ao final)
    with open(caminho_arquivo, 'w') as arquivo:
        registrar_log(f"****registrar_log_tarefa_executada() tarefa_executada = {texto}")
        arquivo.write(texto)

def ler_tarefa_executada():
    try:
        with open('log_tarefa_executada.txt', 'r') as arquivo:
            linhas_tarefa_executada = arquivo.readlines()
            if linhas_tarefa_executada:
                ultimo_tarefa_executada = linhas_tarefa_executada[-1].strip()
                registrar_log(f'****ler_tarefa_executada: {ultimo_tarefa_executada}')
                return ultimo_tarefa_executada
    except FileNotFoundError:
        registrar_log(f'atualizar_tarefa_executada - except FileNotFoundError\ntarefa_executada: {tarefa_executada}')
        ultimo_tarefa_executada = False
        return ultimo_tarefa_executada
    except Exception as e:
        registrar_log(f"atualizar_tarefa_executada - Erro ao ler o contador: \n{e}\ntarefa_executada: {tarefa_executada}")
        ultimo_tarefa_executada = False
        return ultimo_tarefa_executada
    	
def ler_thread_ativa():
    """Lê o arquivo thread_ativa.txt e retorna True ou False."""
    global diretorio_atual
    diretorio_atual = os.getcwd()
    caminho_arquivo = os.path.join(diretorio_atual, 'thread_ativa.txt')
    try:
        with open(caminho_arquivo, 'r') as arquivo:
            conteudo = arquivo.read().strip().upper()
            if conteudo == "TRUE":
                return True
            else:
                return False
    except FileNotFoundError:
        registrar_log("Arquivo thread_ativa.txt não encontrado. Criando com TRUE.")
        escrever_thread_ativa(True)
        return True
    except Exception as erro:
        registrar_log(f"Erro ao ler thread_ativa.txt: {erro}")
        return False
    
def escrever_thread_ativa(valor):
    """Escreve TRUE ou FALSE no arquivo thread_ativa.txt."""
    global diretorio_atual
    diretorio_atual = os.getcwd()
    caminho_arquivo = os.path.join(diretorio_atual, 'thread_ativa.txt')
    try:
        with open(caminho_arquivo, 'w') as arquivo:
            arquivo.write(str(valor).upper())
        registrar_log(f"thread_ativa.txt atualizado para {valor}")
    except Exception as erro:
        registrar_log(f"Erro ao escrever em thread_ativa.txt: {erro}")

def ler_query_sql(nome_arquivo):
    """Lê o conteúdo de um arquivo SQL localizado na mesma pasta do script. """
    global diretorio_atual
    caminho_arquivo = os.path.join(diretorio_atual, nome_arquivo)
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        registrar_log(f"Erro: Arquivo de query '{nome_arquivo}' não encontrado em {caminho_arquivo}.")
        return None
    except Exception as e:
        registrar_log(f"Erro ao ler o arquivo de query '{nome_arquivo}': {e}")
        return None

def encontrar_diretorio_instantclient(nome_pasta="instantclient-basiclite-windows.x64-23.6.0.24.10\\instantclient_23_6"):
  registrar_log(f'Encontrar_diretorio_instantclient')
  # Obtém o diretório base do executável
  base_dir = getattr(sys, '_MEIPASS', os.path.abspath("."))
  registrar_log(f"Caminho base do executavel: {base_dir}")

  # Constrói o caminho completo para a pasta do Instant Client
  caminho_instantclient = os.path.join(base_dir, nome_pasta)
  registrar_log(f'caminho instantclient:\n{caminho_instantclient}')
  # Verifica se a pasta existe
  if os.path.exists(caminho_instantclient):
    return caminho_instantclient
  else:
    registrar_log(f"encontrar diretorio instantclient()\nA pasta '{nome_pasta}' não foi encontrada na raiz do aplicativo.")
    return None

def obter_pacientes_atendimentos():
    try:
        # Chamar a função para obter o caminho do Instant Client
        caminho_instantclient = encontrar_diretorio_instantclient()

        # Usar o caminho encontrado para inicializar o Oracle Client
        if caminho_instantclient:
            oracledb.init_oracle_client(lib_dir=caminho_instantclient)
        else:
            registrar_log("Erro ao localizar o Instant Client. Verifique o nome da pasta e o caminho.")
        
        connection = oracledb.connect( user="PIETRO", password="ATxjWPm", dsn="192.168.5.9:1521/TASYPRD")
        
        with connection:
            with connection.cursor() as cursor:
                # Carrega a query SQL do arquivo
                sql = ler_query_sql('query_obter_pacientes.sql')
                if sql is None:
                    registrar_log("Não foi possível carregar a query SQL. Retornando DataFrame vazio.")
                    return pd.DataFrame() # Retorna um DataFrame vazio para evitar erros

                #Executando a query:
                registrar_log('Executando a query')
                cursor.execute(sql)
                
                # Imprimir os resultados da consulta para verificar
                #registrar_log(f'results = cursor.fetchall()\n')
                results = cursor.fetchall()
        
                #registrar_log(f'df = pd.DataFrame(results, columns=[desc[0] for desc in cursor.description])')
                df = pd.DataFrame(results, columns=[desc[0] for desc in cursor.description])
                
                # Visualizar os primeiros 5 registros
                registrar_log(f'Atendimentos sample: {df.sample()}')
                time.sleep(1)
                registrar_log(f'Atendimentos data frame:{df.shape}')
                time.sleep(1)
                registrar_log("Atendimentos obtido com sucesso!")
                time.sleep(2)

    except Exception as erro:
        registrar_log(f"obter_pacientes_atendimentos() Erro Inesperado:\n{erro}")
    
    #registrar_log(f'return df:{df.head}')
    return df

def Geracao_Pdf_Prescricao(df_):
    #global statusMultiprocessing
    global diretorio_atual_prescricoes
    global lista_nr_atendimento
    global lb_contador
    global tarefa_executada
    global tarefa_executada_erro
    global contador
    #  Geracao_Pdf_Prescricao 
    registrar_log('Geracao de Pdf ()')
    df_filtrado = df_
    registrar_log(f'\ndf_filtrado:\n{df_filtrado.head(1)}')
    
    lb_contador = 0
    contador = 0
    contador_linhas_df = len(df_filtrado)
    registrar_log(f'contador:{contador}\ncontador_linhas_df: {contador_linhas_df}')
    registrar_log_contador(str(contador))
    
    #===== REPETICAO #===== 
    try:
        registrar_log('Inicio da repetição')
        for index, row in df_filtrado.iterrows():
            if not ler_thread_ativa():
                registrar_log("thread_ativa.txt está como FALSE. Interrompendo o loop.")
                break 
            linha = row[0]
            linha = str(linha)
            lista_nr_atendimento.append(linha)
            registrar_log(f'Repeticao for index iterrows()')
            registrar_log(f"Adicionando a lista o nr_atendimento:{linha}")
            registrar_log(f"Geracao Pdf Prescricao - contador:{lb_contador}")
            
            try:
                registrar_log('Geracao_Pdf_Prescricao() - try:')                
                registrar_log('options = Options() # Inicializa as opções do Chrome ')
                options = Options() # Inicializa as opções do Chrome

                registrar_log('Configurações para download automático de PDF')
                # Configurações para download automático de PDF
                prefs = {
                    "download.default_directory": os.path.join(os.path.expanduser("~"), "Downloads"),
                    "download.prompt_for_download": False,
                    "download.directory_upgrade": True,
                    "plugins.always_open_pdf_externally": True # Importante para baixar PDFs diretamente
                }
                registrar_log('options.add_experimental_option("prefs", prefs)')
                options.add_experimental_option("prefs", prefs)

                registrar_log('Maximiza a janela')
                # Maximiza a janela
                options.add_argument("--start-maximized")
                driver = webdriver.Chrome(options=options)

                cpoe_url = obter_configuracao('CPOE', 'url')
                driver.get(cpoe_url)
                registrar_log(f'cpoe_url: {cpoe_url}')
                title = driver.title
                driver.implicitly_wait(TEMPO_ESPERA)

                # Obter credenciais
                registrar_log(f'Obter credenciais: {obter_credenciais_login()}')
                usuario, senha = obter_credenciais_login()

                try:
                    # box de usuario e senha:
                    registrar_log('box de usuario')
                    driver.find_element(By.XPATH, value='//*[@id="loginUsername"]').send_keys(usuario)
                    registrar_log(f'usuario: {usuario}')
                    time.sleep(TEMPO_ESPERA / 5)
                except Exception as e:
                    registrar_log(f"Houve um erro em box de usuario e senha: \n{e}")

                try:
                    registrar_log('box de senha')
                    driver.find_element(By.XPATH, value='//*[@id="loginPassword"]').send_keys(senha)
                    registrar_log(f'senha: {senha}')
                    time.sleep(TEMPO_ESPERA / 5)
                except Exception as e:
                    registrar_log(f"Houve um erro em box de senha: \n{e}")
                
                try:
                    # botao de login:
                    registrar_log('botao de login')
                    bt_login = driver.find_element(By.XPATH, value='//*[@id="loginForm"]/input[3]')
                    bt_login.click()
                    registrar_log('login')
                    driver.implicitly_wait(TEMPO_ESPERA/1.2)
                    time.sleep(TEMPO_ESPERA/1.2)
                except Exception as e:
                    registrar_log(f"Houve um erro em botao de login: \n{e}")

                #try:
                #    #click objeto invalido
                #    registrar_log('click objeto invalido')
                #    pyautogui.click(1107,702)
                #    registrar_log("click objeto invalido\nclick(1107,702)")
                #    driver.implicitly_wait(TEMPO_ESPERA/5)
                #    time.sleep(TEMPO_ESPERA/5)
                #except Exception as e:
                #    registrar_log(f"Houve um erro em click objeto invalido")
                #    time.sleep(TEMPO_ESPERA/1.2)
                    
                try:
                    time.sleep(TEMPO_ESPERA/5)
                    pyautogui.press('enter')
                    registrar_log('1x enter')
                except Exception as e:
                    registrar_log(f"Houve um erro em 1x enter: \n{e}")
                
                try:
                    #clicar no icone do CPOE:
                    registrar_log('clicar no icone do CPOE:')
                    time.sleep(TEMPO_ESPERA/5)
                    bt_CPOE = driver.find_element(By.XPATH, value='//*[@id="app-view"]/tasy-corsisf1/div/w-mainlayout/div/div/w-launcher/div/div/div[1]/w-apps/div/div[1]/ul/li[2]/w-feature-app/a/img')
                    bt_CPOE.click()
                    registrar_log('clicar no CPOE')
                    driver.implicitly_wait(TEMPO_ESPERA*2)
                    time.sleep(TEMPO_ESPERA*2)
                except Exception as e:
                    registrar_log(f"Houve um erro em clicar no CPOE: \n{e}")

                try:                
                    #nr_atendimento
                    pyautogui.write(linha)
                    registrar_log(f'nr_atendimento: {linha}')
                    driver.implicitly_wait(TEMPO_ESPERA/8)
                    time.sleep(TEMPO_ESPERA/8)
                except Exception as e:
                    registrar_log(f"Houve um erro em nr_atendimento: \n{e}")
                
                #enter
                pyautogui.press('enter')
                registrar_log('1 - enter')
                driver.implicitly_wait(TEMPO_ESPERA/2.5)
                time.sleep(TEMPO_ESPERA/2.5)
                
                #enter
                pyautogui.press('enter')
                registrar_log('2 - enter')
                driver.implicitly_wait(TEMPO_ESPERA/2)
                time.sleep(TEMPO_ESPERA/2)
                
                #click atendimento fechado
                pyautogui.click(1100,709)
                registrar_log("click atendimento fechado click(1107,709)")
                driver.implicitly_wait(TEMPO_ESPERA/8)
                time.sleep(TEMPO_ESPERA/8)
                
                try:
                    registrar_log('botao visualizar')
                    #botao visualizar
                    bt_cpoe_relatorios = driver.find_element(By.XPATH, value='//*[@id="handlebar-40"]')
                    bt_cpoe_relatorios.click()
                    registrar_log("bt_cpoe_relatorios.click()")
                    driver.implicitly_wait(TEMPO_ESPERA/10)
                    time.sleep(TEMPO_ESPERA/10)
                except Exception as e:
                    registrar_log(f"Houve um erro em botao visualizar: \n{e}")
                
                try:
                    registrar_log('botao visualizar')
                    #botao visualizar
                    bt_cpoe_visualizar = driver.find_element(By.XPATH, value='//*[@id="popupViewPort"]/li[5]/div[3]')
                    bt_cpoe_visualizar.click()
                    registrar_log("visualizar.click()")
                    #driver.implicitly_wait(TEMPO_ESPERA/8)
                    registrar_log('time.sleep(TEMPO_ESPERA/3)')
                    time.sleep(TEMPO_ESPERA/3)
                except Exception as e:
                    registrar_log(f"Houve um erro em botao visualizar: \n{e}")
                
                #"""Clica no botão 'btn_manter.png' na tela."""
                #try:
                #    # Encontra a localização da imagem do botão na tela
                #    registrar_log("tentando clicar no btn_manter()")
                #    localizacao = pyautogui.locateOnScreen('btn_manter.png', confidence=0.95)
                #    # Encontra o centro da localização:
                #    ponto_central = pyautogui.center(localizacao)
                #    # Move o mouse para o centro da imagem e clica
                #    registrar_log(f"localizacao:{localizacao}\nponto_central:{ponto_central}")
                #    pyautogui.click(ponto_central)
                #    time.sleep(TEMPO_ESPERA/8)
                #    registrar_log(f"btn_manter.png click(ponto_central)")
                #except pyautogui.ImageNotFoundException:
                #    registrar_log("Imagem 'btn_manter.png' não encontrada na tela.")
                #except Exception as e:
                #    registrar_log(f"Houve um erro em clicar_btn_manter: \n{e}")
                #time.sleep(TEMPO_ESPERA/8)  
                #
                #registrar_log('click no baixar')

                ## Clicar no botão de download usando Selenium com By.ID
                #try:
                #    registrar_log(f'Tentando clicar no botão "Baixar" (ID: download)')
                #    # Espera explícita para o botão de download ficar clicável
                #    download_button = WebDriverWait(driver, TEMPO_ESPERA).until(
                #        EC.element_to_be_clickable((By.ID, "download"))
                #    )
                #    download_button.click()
                #    registrar_log(f'Botão "Baixar" clicado via Selenium.')
                #    time.sleep(TEMPO_ESPERA/5) # Pequena pausa para o download iniciar
                #except TimeoutException: # type: ignore
                #    registrar_log("Erro: Botão 'Baixar' (ID: download) não encontrado ou não clicável após o tempo de espera.")
                #    # Se o botão não for encontrado, pode ser que o PDF já tenha sido baixado automaticamente
                #    # ou que o elemento tenha mudado.
                #    # Considere adicionar uma lógica alternativa aqui se necessário.
                #except Exception as e:
                #    registrar_log(f"Erro inesperado ao clicar no botão 'Baixar': {e}")
                
                # Obter coordenadas do botão "manter" do config.ini
                try:
                    manter_x_str = obter_configuracao('UI_COORDINATES', 'manter_x')
                    manter_y_str = obter_configuracao('UI_COORDINATES', 'manter_y')
                    manter_x = int(manter_x_str)
                    manter_y = int(manter_y_str)
                    registrar_log(f"Coordenadas do botão 'Manter' lidas do config.ini: ({manter_x}, {manter_y})")
                    registrar_log('click no manter')
                    pyautogui.click(manter_x, manter_y)

                except (ValueError, TypeError):
                    registrar_log("Erro ao ler/converter coordenadas do config.ini. Usando valores padrão (1755, 106).")
                    manter_x, manter_y = 1755, 106

                
                #registrar_log(f'manter.click({manter_x}, {manter_y})')
                #time.sleep(TEMPO_ESPERA/5)
                #
                ##click no manter
                #registrar_log(f'btn_manter')
                #pyautogui.click(manter_x, manter_y)
                #registrar_log(f'manter.click({manter_x}, {manter_y})')
                #time.sleep(TEMPO_ESPERA/5)
                #
                ##click no manter
                #registrar_log(f'btn_manter')
                #pyautogui.click(manter_x, manter_y)
                #registrar_log(f'manter.click({manter_x}, {manter_y})')
                #time.sleep(TEMPO_ESPERA/5)
                
                registrar_log('time.sleep(TEMPO_ESPERA)')
                time.sleep(TEMPO_ESPERA/3)
                
                registrar_log(f'\ndriver.quit()\n')
                driver.quit()

                
                try:
                    registrar_log('acessando pasta download:')
                    #acessando pasta download:
                    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
                    registrar_log(f'Caminho da pasta download: {downloads_path}')
                    time.sleep(TEMPO_ESPERA/5)
                except Exception as e:
                    registrar_log(f"Houve um erro em acessar pasta download: \n{e}")
                    time.sleep(TEMPO_ESPERA/5)
                
                try:
                    registrar_log('verificando arquivos da pasta download:')
                    #verificando arquivos da pasta download
                    files = [f for f in os.listdir(downloads_path) if f.endswith('.pdf')]
                    registrar_log(f"Arquivos:\n{files}")
                    time.sleep(TEMPO_ESPERA/5)
                except Exception as e:
                    registrar_log(f"Houve um erro em verificar arquivos da pasta download: \n{e}")  
                
                try:
                    registrar_log('ultimo arquivo antes de renomear:')
                    #ultimo arquivo
                    ultimo_arquivo = os.path.join(downloads_path, files[0])
                    registrar_log(f"Ultimo arquivo antes de renomear: {ultimo_arquivo}")
                    time.sleep(TEMPO_ESPERA/5)
                except Exception as e:
                    registrar_log(f"Houve um erro em ultimo")
                
                try:
                    # Caminho da pasta Prescricoes
                    pasta_prescricoes = "Prescricoes"
                    registrar_log(f"pasta_prescricoes: {pasta_prescricoes}")
                    time.sleep(TEMPO_ESPERA/5)
                except Exception as e:
                    registrar_log(f"Houve um erro em pasta_prescricoes")
               
                try:
                    # Cria a pasta da data se não existir                                    
                    pasta_data = os.path.join(pasta_prescricoes, agora_limpo())
                    registrar_log(f"pasta_data: {pasta_data}")
                    time.sleep(TEMPO_ESPERA/5)
                except Exception as e:
                    registrar_log(f"Houve um erro em pasta_data")
                
                try:                    
                    # Cria a pasta da data se não existir
                    os.makedirs(pasta_data, exist_ok=True)
                    registrar_log(f"Cria a pasta da data se não existir: {pasta_data}")
                    time.sleep(TEMPO_ESPERA/5)
                except Exception as e:
                    registrar_log(f"Houve um erro em criar a pasta da data se não existir")
                
                try:
                    registrar_log('renomeia e move os arquivos')
                    registrar_log(f"Data_hora: {agora()}")
                    caminho_antigo = os.path.join(downloads_path, ultimo_arquivo)
                    registrar_log(f"caminho antigo: {caminho_antigo}")
                    nr_atendimento = linha
                    caminho_novo = os.path.join(pasta_data, f"{nr_atendimento} - {agora().replace(':', '-')}.pdf")
                    registrar_log(f'caminho_novo = {caminho_novo},arquivo:{agora().replace(':', '-')}.pdf)')
                except Exception as e:
                    registrar_log(f"Houve um erro em renomeia e move os arquivos: \n{e}")
            
                try:
                    registrar_log(f'try: shutil.move(\n time.sleep(TEMPO_ESPERA/5)')
                    time.sleep(TEMPO_ESPERA/5)
                    registrar_log(f'caminho_antigo:{caminho_antigo}, \ncaminho_novo{caminho_novo})')
                    shutil.move(caminho_antigo, caminho_novo)
                    registrar_log(f"Arquivo:{caminho_novo} Renomeado e movido com sucesso.")
                except shutil.Error as e:
                    registrar_log(f"Erro ao mover o arquivo: {e}")
                    tarefa_executada_erro = True
                    
                time.sleep(TEMPO_ESPERA/5)
                #FIM
                contador += 1
                lb_contador = contador
                registrar_log(f'Contador: {contador}')
                registrar_log_contador(str(contador))
                #se rodar tudo ok, retirar o número de atendimento da lista_nr_atendimento
                lista_nr_atendimento.remove(linha)
                registrar_log(f'lista_nr_atendimento.remove({linha})')
                registrar_log(f'******************** FIM do {linha} ********************')
                
                # pausa dramática:
                time.sleep(TEMPO_ESPERA/8)
                
            except Exception as erro:
                    registrar_log(f'except do try de dento do for linha in df_filtrado')
                    #driver.quit()
                    driver.quit()
                    registrar_log(f'\ndriver.quit()\n')
                    registrar_log(f'\nlista_nr_atendimento:{lista_nr_atendimento}\ncontador: {contador} \n=========== ERROR:\n{erro}')
    
    except Exception as erro:
        #ao terminar extoura um exception e cai nesse bloco
        registrar_log(f"=========== \nERROR:\n except: for linha in df_filtrado:\nlista_nr_atendimento:{lista_nr_atendimento}\ncontador: {contador} \n{erro}")                    
    finally:
         #se ocorrer um erro na execução, definimos que a variavel tarefa_executada sera False para que a tarefa possa ser executada novamente:
         if not tarefa_executada_erro:
            tarefa_executada = True
            registrar_log(f'tarefa_executada: {tarefa_executada}')
            registrar_log(f'tarefa_executada_erro: {tarefa_executada_erro}')
            registrar_log(f'se ocorrer um erro na execução\ndefinimos que a variavel tarefa_executada sera False\n para que a tarefa possa ser executada novamente:')
    try:
        registrar_log(f'===== try:\nLista com nr_atendimentos com erro')
        #montar data frame com lista de itens que tiveram erro e não foram deletados:
        df_lista_nr_atendimento = pd.DataFrame(lista_nr_atendimento)
        lista_nr_atendimento = []
        #registrar_log(f'Lista com nr_atendimentos com erro APAGADA!\nlista_nr_atendimento: {lista_nr_atendimento}')
        #registrar_log(f'df_lista_nr_atendimento: {df_lista_nr_atendimento}')
        
        #ação para o caso do df_lista_nr_atendimento for vazio ou não:
        if df_lista_nr_atendimento.empty:
            registrar_log(f'\nTodos os atendimentos foram gerados com sucesso!')
            #registrar_log(f'FIM Geracao_Pdf_Prescricao()')
            df_lista_nr_atendimento = None
            df_renovo = df_lista_nr_atendimento
            #registrar_log(f'if df_lista_nr_atendimento.empty:{df_lista_nr_atendimento}\ndf:{df}')
        else:
            registrar_log(f'ação para o caso do df_lista_nr_atendimento não for vazio\ndf_lista_nr_atendimento nao esta em branco\n')
            registrar_log(f'global df recebera df_lista_nr_atendimento!!!!')
            registrar_log(f'df = df_lista_nr_atendimento:\n{df_lista_nr_atendimento}')
            df_renovo = df_lista_nr_atendimento
            registrar_log_atend_erros(f'df_lista_nr_atendimento.shape: {df_lista_nr_atendimento.shape}')
            df_lista_nr_atendimento = None
            registrar_log(f'df atendimentos com erro df_renovo.shape: {df_renovo.shape}')
            registrar_log(f"Executara novamente a Geracao_Pdf_Prescricao() com o global df apenas com os nr_atendimento que tiveram erros:")
            Geracao_Pdf_Prescricao(df_renovo)
            
        #copiar_arquivos:
        registrar_log(f'def Geracao_PDF_Prescricao() \nbloco com funcao copiar_arquivos()')
        copiar_arquivos()

            
        #FIM:
        #statusMultiprocessing = False
        df_ = []
        registrar_log(f'df_: \n{df_}')
        #registrar_log(f'\n #FIM Geracao_Pdf_Prescricao(df_)\nstatusMultiprocessing = {statusMultiprocessing}')

        registrar_log(f"Geracao Pdf Prescricao\nANTES:\nTarefa_executada: {tarefa_executada}\nTarefa_executada_erro:{tarefa_executada_erro}")

        tarefa_executada = False

        registrar_log(f"Geracao Pdf Prescricao\nDEPOIS:\nTarefa_executada: {tarefa_executada}\nTarefa_executada_erro:{tarefa_executada_erro}")
    except Exception as erro:
        registrar_log(f"ERROR:\n except: {erro}") 

    registrar_log(f'FIM Geracao_Pdf_Prescricao(df_)\n')

def cronometro_tarefa_agendada():
    """Executa a tarefa agendada periodicamente"""
    global thread_ativa
    registrar_log(f'cronometro_tarefa_agendada()')

    # Agendamentos:
    schedule.every().day.at("00:00:01").do(main)
    schedule.every().day.at("12:00:01").do(main)
    registrar_log(f'Planejada execução todos os dias às 00:00 e 12:00')

    while thread_ativa:
        schedule.run_pending()
        time.sleep(1)
        registrar_log_cronometro(f'Execução agendada para todos os dias às 00:00 e 12:00')

    registrar_log("Thread de agendamento finalizada!")
    registrar_log("FIM DA EXECUÇÃO!")

def copiar_arquivos():
    """Copia todos os arquivos e subdiretórios de uma pasta para outra."""
    registrar_log(f'def copiar_arquivos()')
    
    # Obter o diretório base do arquivo executável:
    base_dir = getattr(sys, '_MEIPASS', os.path.abspath("."))
    registrar_log(f'base_dir: {base_dir}')
    
    origem = os.path.join(base_dir,"Prescricoes") # A pasta Prescricoes esta na raiz do projeto
    #destino = "\\\\192.168.103.252\\tihsf$\\PIETRO\\Projetos\\RPA_PRESCR_EM_PDF\\Prescricoes"
    destino = "\\\\192.168.103.252\\contingencia_hsf$\\Impressos\\Prescricoes"
    
    registrar_log(f'Caminho de origem: {origem}')
    registrar_log(f'Caminho de destino: {destino}')
    
    try:
        registrar_log(f'shutil.copytree(origem, destino, dirs_exist_ok=True)')
        shutil.copytree(origem, destino, dirs_exist_ok=True)
        registrar_log(f"\nArquivos copiados com sucesso \nde: {origem} \npara {destino}\nFIM copiar_arquivos()")
    except FileExistsError:
        registrar_log(f"\nA pasta de destino {destino} ja existe. Verifique se deseja sobrescrever.\nFileExistsError copiar_arquivos()")
    except Exception as e:
        registrar_log(f"\nOcorreu um erro durante a cópia: {str(e)}\nException copiar_arquivos()\n{e}")

def ao_fechar():
    """Finaliza corretamente a aplicação e todas as threads"""
    global thread_ativa, threadExecutar
    registrar_log(f"thread_ativa: {thread_ativa}")
    registrar_log("Fechando aplicação...")

    # Escreve FALSE no arquivo thread_ativa.txt
    escrever_thread_ativa(False)

    # Para a execução da thread
    thread_ativa = False

    # Aguarda a thread terminar
    if threadExecutar is not None and threadExecutar.is_alive():
        threadExecutar.join(timeout=2)

    # Fecha a janela do Tkinter
    janela.destroy()

    # Finaliza o processo completamente
    sys.exit()

def atualizar_log():
    global lb_contador
    """Atualiza o rótulo do log com a última linha do arquivo log.txt."""
    try:
        with open('log.txt', 'r') as arquivo:
            linhas = arquivo.readlines()
            if linhas:
                ultima_linha = linhas[-1].strip() #pega a última linha, e remove os espaços
                label_status['text'] = ultima_linha
                label_status.update_idletasks()
                if "lb_contador" in ultima_linha:
                     lb_contador = ultima_linha.split("lb_contador:")[1].split(" - linha:")[0].strip() #extraindo o lb_contador do texto
                     label_status_lb_contador['text'] = str(lb_contador)
    except FileNotFoundError:
        label_log['text'] = "Arquivo de log não encontrado."
    except Exception as e:
          label_log['text'] = f"Erro ao ler o log: {e}"
    finally:
        janela.after(2000, atualizar_log) # agendar para rodar daqui 2 segundos;

def atualizar_contador():
    global lb_contador
    """Atualiza o rótulo do contador com a última linha do arquivo log_contador.txt."""
    try:
        with open('log_contador.txt', 'r') as arquivo:
            linhas_contador = arquivo.readlines()
            if linhas_contador:
                ultimo_contador = linhas_contador[-1].strip()
                label_status_lb_contador['text'] = f'Contador: {ultimo_contador}'  # Atualiza o texto do label com o contador
    except FileNotFoundError:
        label_status_lb_contador['text'] = "Arquivo do contador não encontrado."
    except Exception as e:
        label_status_lb_contador['text'] = f"Erro ao ler o contador: {e}"
    finally:
        janela.after(2000, atualizar_contador)
    
def main():
    #global statusMultiprocessing
    global df
    global lb_contador
    global df_filtrado
    global tarefa_executada
    global tarefa_executada_erro
    global janela # adicionei global janela
    global bt_executar
    
    registrar_log("Main()")
    encontrar_diretorio_instantclient()
    df_filtrado  = obter_pacientes_atendimentos()
    registrar_log(f"Main() df_filtrado tamanho: {df_filtrado.shape}")
    registrar_log(f'Geracao_Pdf_Prescricao({df_filtrado.shape})')
    Geracao_Pdf_Prescricao(df_filtrado)
    
    if not tarefa_executada_erro:
         registrar_log("Prescrições geradas!")
         label_status['text'] = "Prescrições geradas!" # Alterar a label para informar que a tarefa foi finalizada
         bt_executar.config(state="normal") # Reabilita o botão
         registrar_log_tarefa_executada('True')
    else:
         tarefa_executada_erro = False
    registrar_log("FIM DA EXECUÇÃO")

def planejar():
    """Inicia a execução da tarefa agendada em uma nova thread"""
    global tarefa_agendada_iniciada, threadExecutar
    registrar_log("def planejar()")

    if not tarefa_agendada_iniciada:
        registrar_log(f"Botão Planejar clicado!")
        label_status['text'] = "Tarefa Agendada Inicializada!"  
        tarefa_agendada_iniciada = True
        bt_Planejar.config(state="disabled")  # Desabilita o botão de planejamento
        #adicionado o daemon=True
        threadExecutar = threading.Thread(target=cronometro_tarefa_agendada, daemon=True)
        threadExecutar.start()
    else:
        registrar_log('Tarefa planejada já inicializada')
        label_status['text'] = "Tarefa Agendada Já Inicializada!"

def executar():
    global df_filtrado
    global df
    global lb_contador
    global tarefa_executada
    global tarefa_executada_erro
    registrar_log(f"Botao executar clicado! - tarefa executada: {tarefa_executada}, tarefa_executada_erro:{tarefa_executada_erro}")
    if not tarefa_executada:
        tarefa_executada = True
        tarefa_executada_erro = False
        label_status['text'] = "Tarefa inicializada!"
        registrar_log(f'Tarefa inicializada! \nbt_executar desativado!')    
        bt_executar.config(state="disabled")  # desabilita o botão
        threadExecutar = threading.Thread(target=main).start()
    else:
        registrar_log("Tarefa já executada ou planejada não inicializada. Ignorando clique.")
        label_status['text'] = "Tarefa ja executada ou planejada não inicializada!" 

if __name__ == "__main__":
    try:
        registrar_log(f'{agora()}\n__name__ == "__main__" \n')
        
        #deletando todos os arquivos da pasta download
        pasta_downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        #registrar_log(f'deletando todos os arquivos da pasta download\npasta_downloads = os.path.join(os.path.expanduser("~"), "Downloads")\n')
        registrar_log_tarefa_executada('False')

        registrar_log(" Inicio() ")

        #cria o arquivo thread_ativa.txt
        escrever_thread_ativa(True)
        
        #INTERFACE GRAFICA:
        janela = tk.Tk()
        janela.maxsize(600,400)
        janela.geometry('600x400')
        
        #titulo do app
        janela.title("PDD")
        
        # Associa a função ao_fechar ao evento de fechamento da janela
        janela.protocol("WM_DELETE_WINDOW", ao_fechar)
        
        #imagem do HSF em 60x77
        imagem = tk.PhotoImage(file='HSF_LOGO_-_60x77_001.png', height=60, width=77)
        lb_imagem = tk.Label(janela, image=imagem)
        lb_imagem.place(x=20, y=10)
        
        titulo_label = tk.Label(janela, text='APP GERADOR DE PRESCRIÇÕES POR SETOR', font=('Arial',12))
        titulo_label.place(x=135, y=33.5)
        
        # Criando um frame para centralizar o conteúdo
        frame_central = tk.Frame(janela)
        frame_central.place(relx=0.5, rely=0.5, anchor='center')
        
        # Rótulo para mostrar o status
        label_status = tk.Label(frame_central, text="...", wraplength=550, justify="center")
        label_status.pack(expand=True, fill='both') # Usando pack para centralizar horizontalmente
        
        # Criar um frame para colocar os botoes lado a lado
        frame_botoes = tk.Frame(frame_central)
        frame_botoes.pack()
        
        bt_Planejar = tk.Button(frame_botoes, width=18, text="Planejar Tarefa",command=lambda: [
                                                                                            planejar(),
                                                                                            label_status.config(text="Tarefa planejada inicializada!"),
                                                                                            
                                                                                            ])
        bt_Planejar.pack(side=tk.LEFT, padx=40 , pady = 40)

        bt_executar = tk.Button(frame_botoes, width=18, text="Executar Tarefa", command=lambda: [
                                                                                            executar(),
                                                                                            label_status.config(text="Tarefa executada inicializada!"),
                                                                                            ])
        bt_executar.pack(side=tk.LEFT, padx=40, pady = 40)
        
        PLima_label = tk.Label(janela, text='@PLima', font=('Arial',4))
        PLima_label.place(x=565, y=387)
        
        # Rótulo para exibir a última linha do log
        label_log = tk.Label(janela, text="", wraplength=550, justify="left") #justify para alinhar a esquerda
        label_log.place(x=25, y=80)
        
        # Rótulo para exibir lb_contador no rodapé
        label_status_lb_contador = tk.Label(janela, text=f"Contador: {str(lb_contador)}", font=('Arial', 8))
        label_status_lb_contador.place(x=260, y=370)  # Posiciona no rodapé
        
        # Executar a função para atualizar o log
        atualizar_log()
        
        # Iniciar a atualização do contador
        atualizar_contador()
        
        janela.mainloop()
            
    except Exception as erro:
        registrar_log(f'"__main__"\nException Error: \n{erro}')
