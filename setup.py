"""
10/01/2025
@PLima

Automação PDID - Setup.py necessario para criação de exe
"""

import sys
from cx_Freeze import setup, Executable

# Lista de arquivos/pastas que devem ser incluídos no pacote .exe
includefiles = ["HSF_LOGO_-_60x77_001.png", 'log.txt', 'log_cronometro.txt', 'log_atend_erros.txt', 'log_contador.txt', 'instantclient-basiclite-windows.x64-23.6.0.24.10\\instantclient_23_6', 'btn_manter.png']

build_exe_options = {"packages": ["os"], "includes": [
                                                        "datetime",
                                                        "tkinter",
                                                        "os",
                                                        "selenium",
                                                        "time",
                                                        "pyautogui",
                                                        "pandas",
                                                        "glob",
                                                        "shutil",
                                                        "schedule",
                                                        "multiprocessing",
                                                        "oracledb",
                                                        "sys"
                                                    ]
                    }
#bibliotecas a serem incluidas
#include_msvcr = ['msvcp140.dll','vcruntime140.dll', 'vcruntime140_1.dll', 'vcruntime140_2.dll']

base = None
if sys.platform == "win32":
    base = "Win32GUI"

# Configuração da sua aplicação
setup(
    name="PDD",  # Nome do seu aplicativo
    version="1.0",  # Versão do aplicativo
    description="App Gerador de Prescrições em pdf",  # Descrição do aplicativo
    options={
             "build_exe": build_exe_options},
    executables=[Executable("main.py",icon ="icone.ico", base=base if sys.platform == "win32" else None)]
)