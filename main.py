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
import os
import pandas as pd
import os
import glob
import shutil
import schedule
import multiprocessing
import oracledb
import sys
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
    	
def excluir_arquivos_past_downloads():
    registrar_log(f'Excluir_arquivos_past_downloads()')
    #acessando pasta download:
    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
    registrar_log(f'Caminho da pasta downloads: {downloads_path}')    
    files = glob.glob(os.path.join(downloads_path, '*'))
    for f in files:
        try:
            os.remove(f)
            registrar_log(f"Arquivo {f} removido com sucesso.")
        except Exception as e:
            registrar_log(f"Não foi possível remover o arquivo {f}\nErro: {e}\n")          

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
            print("Erro ao localizar o Instant Client. Verifique o nome da pasta e o caminho.")
        
        connection = oracledb.connect( user="PIETRO", password="ATxjWPm", dsn="192.168.5.9:1521/TASYPRD")
        
        with connection:
            with connection.cursor() as cursor:
                #####################################################################################
                #QUERY:
                sql = """ 
                        SELECT 
                            APV.NR_ATENDIMENTO
                        FROM ATENDIMENTO_PACIENTE_V APV
                        LEFT JOIN prescr_medica PM ON (  PM.NR_ATENDIMENTO = APV.NR_ATENDIMENTO )
                        LEFT JOIN prescr_mat_hor PH ON ( PH.NR_PRESCRICAO = PM.NR_PRESCRICAO)
                        WHERE APV.DT_ALTA IS NULL
                        --AND APV.IE_STATUS_ATENDIMENTO = 'E'
                        And	PH.dt_horario between SYSDATE -1 and SYSDATE
                        and APV.CD_SETOR_ATENDIMENTO not in (  171 )
                        GROUP BY 
                            APV.NR_ATENDIMENTO,
                            APV.CD_SETOR_ATENDIMENTO,
                            APV.CD_PESSOA_FISICA
                        ORDER BY 
                            APV.CD_SETOR_ATENDIMENTO
                        FETCH FIRST 1 ROWS ONLY
                    """
                #####################################################################################
                
                #Executando a query:
                cursor.execute(sql)
                
                # Imprimir os resultados da consulta para verificar
                #registrar_log(f'results = cursor.fetchall()\n')
                results = cursor.fetchall()
        
                #registrar_log(f'df = pd.DataFrame(results, columns=[desc[0] for desc in cursor.description])')
                df = pd.DataFrame(results, columns=[desc[0] for desc in cursor.description])
                
                # Visualizar os primeiros 5 registros
                registrar_log(f'Atendimentos: {df.sample()}')
                time.sleep(2)
                registrar_log(f'Atendimentos data frame:{df.shape}')
                time.sleep(2)
                registrar_log("Atendimentos obtido com sucesso!")
                time.sleep(5)

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
            linha = row[0]
            linha = str(linha)
            lista_nr_atendimento.append(linha)
            registrar_log(f'Repeticao for index iterrows()')
            registrar_log(f"Adicionando a lista o nr_atendimento:{linha}")
            registrar_log(f"Geracao Pdf Prescricao - contador:{lb_contador}")
            
            try:
                registrar_log('Geracao_Pdf_Prescricao() - try:')                
                #tela toda:
                driver = webdriver.Chrome()
                options = Options()
                options.add_argument("--start-maximized")
                driver = webdriver.Chrome(options=options)
                driver.get("http://aplicacao.hsf.local:7070/#/login")
                registrar_log('http://aplicacao.hsf.local:7070/#/login')
                title = driver.title
                driver.implicitly_wait(TEMPO_ESPERA)
                
                # box de usuario:
                box_usuario = driver.find_element(By.XPATH, value='//*[@id="loginUsername"]')
                box_usuario.send_keys('pvplima')
                registrar_log('usuario')
                time.sleep(TEMPO_ESPERA/5)
                
                # box de senha:
                box_senha = driver.find_element(By.XPATH, value='//*[@id="loginPassword"]')
                box_senha.send_keys('hsf@2024')
                registrar_log('senha')
                time.sleep(TEMPO_ESPERA/5)
                
                # botao de login:
                bt_login = driver.find_element(By.XPATH, value='//*[@id="loginForm"]/input[3]')
                bt_login.click()
                registrar_log('login')
                driver.implicitly_wait(TEMPO_ESPERA/1.2)
                time.sleep(TEMPO_ESPERA/1.2)
                
                #click objeto invalido
                pyautogui.click(1107,702)
                registrar_log("click objeto invalido\nclick(1107,702)")
                driver.implicitly_wait(TEMPO_ESPERA/5)
                time.sleep(TEMPO_ESPERA/5)
        
                #clicar no icone do CPOE:
                bt_CPOE = driver.find_element(By.XPATH, value='//*[@id="app-view"]/tasy-corsisf1/div/w-mainlayout/div/div/w-launcher/div/div/div[1]/w-apps/div/div[1]/ul/li[2]/w-feature-app/a/img')
                bt_CPOE.click()
                registrar_log('clicar no CPOE')
                driver.implicitly_wait(TEMPO_ESPERA*2)
                time.sleep(TEMPO_ESPERA*2)
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
                
                #botao visualizar
                bt_cpoe_relatorios = driver.find_element(By.XPATH, value='//*[@id="handlebar-40"]')
                bt_cpoe_relatorios.click()
                registrar_log("bt_cpoe_relatorios.click()")
                driver.implicitly_wait(TEMPO_ESPERA/10)
                time.sleep(TEMPO_ESPERA/10)
                
                #botao visualizar
                bt_cpoe_visualizar = driver.find_element(By.XPATH, value='//*[@id="popupViewPort"]/li[5]/div[3]')
                bt_cpoe_visualizar.click()
                registrar_log("visualizar.click()")
                driver.implicitly_wait(TEMPO_ESPERA)
                time.sleep(TEMPO_ESPERA)

                """Clica no botão 'btn_manter.png' na tela."""
                registrar_log("tentando clicar no btn_manter()")
                try:
                    # Encontra a localização da imagem do botão na tela
                    localizacao = pyautogui.locateOnScreen('btn_manter.png', confidence=0.95)
                    # Encontra o centro da localização:
                    ponto_central = pyautogui.center(localizacao)
                    # Move o mouse para o centro da imagem e clica
                    registrar_log(f"localizacao:{localizacao}\nponto_central:{ponto_central}")
                    pyautogui.click(ponto_central)
                    time.sleep(TEMPO_ESPERA/8)
                    registrar_log(f"btn_manter.png click(ponto_central)")
                except pyautogui.ImageNotFoundException:
                    registrar_log("Imagem 'btn_manter.png' não encontrada na tela.")
                except Exception as e:
                    registrar_log(f"Houve um erro em clicar_btn_manter: \n{e}")
                time.sleep(TEMPO_ESPERA/8)  

                #click no baixar
                registrar_log(f'click no baixar')
                pyautogui.click(1817,165)
                registrar_log(f'baixar.click(1817,165)')
                time.sleep(TEMPO_ESPERA/5)
                
                #Pressionar enter:
                pyautogui.press('enter')
                registrar_log("Pressionar('enter')")
                time.sleep(TEMPO_ESPERA/5)  
                            
                #click no manter
                registrar_log(f'btn_manter')
                pyautogui.click(1755,106)
                registrar_log(f'manter.click(1755,106)')
                time.sleep(TEMPO_ESPERA/5)
                
                #click no manter
                registrar_log(f'btn_manter')
                pyautogui.click(1755,106)
                registrar_log(f'manter.click(1751,112)')
                time.sleep(TEMPO_ESPERA/5)
                
                #click no manter
                registrar_log(f'btn_manter')
                pyautogui.click(1755,106)
                registrar_log(f'manter.click(1755,106)')
                time.sleep(TEMPO_ESPERA/5)
                
                #driver.quit()
                driver.quit()
                registrar_log(f'\ndriver.quit()\n')
                
                #registrar_log(f'contador = {contador} - de contador_linhas_df:{contador_linhas_df}')
                
                #acessando pasta download:
                downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
                registrar_log(f'Caminho da pasta download: {downloads_path}')
                time.sleep(TEMPO_ESPERA/5)
                
                #verificando arquivos da pasta download
                files = [f for f in os.listdir(downloads_path) if f.endswith('.pdf')]
                registrar_log(f"Arquivos:\n{files}")
                time.sleep(TEMPO_ESPERA/5)
                
                #ultimo arquivo
                ultimo_arquivo = os.path.join(downloads_path, files[0])
                registrar_log(f"Ultimo arquivo antes de renomear: {ultimo_arquivo}")
                time.sleep(TEMPO_ESPERA/5)
                
                # Caminho da pasta Prescricoes
                pasta_prescricoes = "Prescricoes"
                registrar_log(f"pasta_prescricoes: {pasta_prescricoes}")
                time.sleep(TEMPO_ESPERA/5)
                
                pasta_data = os.path.join(pasta_prescricoes, agora_limpo())
                registrar_log(f"pasta_data: {pasta_data}")
                time.sleep(TEMPO_ESPERA/5)
                
                # Cria a pasta da data se não existir
                os.makedirs(pasta_data, exist_ok=True)
                registrar_log(f"Cria a pasta da data se não existir: {pasta_data}")
                time.sleep(TEMPO_ESPERA/5)
                
                #renomeia e move os arquivos
                registrar_log(f"Data_hora: {agora()}")
                caminho_antigo = os.path.join(downloads_path, ultimo_arquivo)
                registrar_log(f"caminho antigo: {caminho_antigo}")
                nr_atendimento = linha
                caminho_novo = os.path.join(pasta_data, f"{nr_atendimento} - {agora().replace(':', '-')}.pdf")
                registrar_log(f'caminho_novo = {caminho_novo},arquivo:{agora().replace(':', '-')}.pdf)')
            
                try:
                    time.sleep(TEMPO_ESPERA/5)
                    registrar_log(f'try: shutil.move(\ncaminho_antigo:{caminho_antigo}, \ncaminho_novo{caminho_novo})')
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
                #registrar_log(f'lista_nr_atendimento.remove({linha})')
                #registrar_log(f'Retirando da lista o nr_atendimento: {linha}')
                #registrar_log(f'lista_nr_atendimento:\n{lista_nr_atendimento}')
                #registrar_log(f'\ncontador = {contador} - de contador_linhas_df:{contador_linhas_df}')
                #registrar_log(f'******************** FIM ********************')
                
                # pausa dramática:
                time.sleep(TEMPO_ESPERA/5)
                
            except Exception as erro:
                    registrar_log(f'=========== \nERROR:\nexcept do try de dento do for linha in df_filtrado')
                    registrar_log(f'\nlista_nr_atendimento:{lista_nr_atendimento}\ncontador: {contador} \n{erro}')
    
    except Exception as erro:
        #ao terminar extoura um exception e cai nesse bloco
        registrar_log(f"=========== \nERROR:\n except: for linha in df_filtrado:\nlista_nr_atendimento:{lista_nr_atendimento}\ncontador: {contador} \n{erro}")                    
    finally:
         #se ocorrer um erro na execução, definimos que a variavel tarefa_executada sera False para que a tarefa possa ser executada novamente:
         if not tarefa_executada_erro:
            tarefa_executada = True

    #registrar_log(f'Lista com nr_atendimentos com erro\nlista_nr_atendimento: {lista_nr_atendimento}')
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
        df = df_lista_nr_atendimento
        #registrar_log(f'if df_lista_nr_atendimento.empty:{df_lista_nr_atendimento}\ndf:{df}')
    else:
        #registrar_log(f'df_lista_nr_atendimento nao esta em branco\nglobal df recebera df_lista_nr_atendimento!!!!')
        #registrar_log(f'\ndf = df_lista_nr_atendimento: \n{df_lista_nr_atendimento}')
        df = df_lista_nr_atendimento
        df_lista_nr_atendimento = None
        #registrar_log(f'df_lista_nr_atendimento.clear(){df_lista_nr_atendimento.sample()}')
        #registrar_log(f'df = df: \n{df.sample()}')
        #registrar_log_atend_erros(df)
        registrar_log(f"Executara novamente a Geracao_Pdf_Prescricao() com o global df apenas com os nr_atendimento que tiveram erros:")
        
        #TODO: ALT + F4
        pyautogui.press("alt","f4")
        registrar_log('pyautogui.press("alt","f4")')

        Geracao_Pdf_Prescricao(df)
        
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
    
    registrar_log(f'FIM Geracao_Pdf_Prescricao(df_)\n')

def cronometro_tarefa_agendada():
    registrar_log(f'cronometro_tarefa_agendada()')
    
    #agendamentos:
    schedule.every().day.at("00:00:01").do(main)
    schedule.every().day.at("12:00:01").do(main)
    registrar_log(f'Planejada execução todos os dia as 00:00 e 12:00')
    #inserindo o schedule
    while True:
        schedule.run_pending()
        time.sleep(1)
        registrar_log_cronometro(f'Planejada execucao todos os dia as 00:00 e 12:00')

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
    #resultado = messagebox.askyesno("Confirmação", "Tem certeza de que deseja fechar o aplicativo?")
    #if resultado:
    #    # Feche o aplicativo
    #    janela.destroy()
    #Função chamada quando o usuário clica no botao 'X' para fechar a janela.
    registrar_log(f'statusMultiprocessing:{statusMultiprocessing}')
    registrar_log("O aplicativo foi fechado no botao X\n")
    janela.destroy()
    time.sleep(0.5)
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
    excluir_arquivos_past_downloads()
    encontrar_diretorio_instantclient()
    df_filtrado  = obter_pacientes_atendimentos()
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
    global df_filtrado
    global df
    global tarefa_agendada_iniciada
    registrar_log(" def planejar()")
    if not tarefa_agendada_iniciada:
        registrar_log(f"Botao Iniciar clicado!")
        label_status['text'] = "Tarefa Agendada Inicializada!"  
        tarefa_agendada_iniciada = True
        bt_Planejar.config(state="disabled") # desabilitando o botão de planejar a tarefa
        threadExecutar = threading.Thread(target=cronometro_tarefa_agendada).start()
    else:
        registrar_log('Tarefa planejada ja inicializada')
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