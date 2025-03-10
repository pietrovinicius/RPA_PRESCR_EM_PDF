"""
10/01/2025
@PLima

Automação PDD - Setup.py para criação do executável (.exe)
"""

import sys
from cx_Freeze import setup, Executable

# Lista de arquivos/pastas que devem ser incluídos no pacote .exe
includefiles = ["HSF_LOGO_-_60x77_001.png", '.', 'instantclient-basiclite-windows.x64-23.6.0.24.10\instantclient_23_6', 'btn_manter.png', 'icone.ico']

build_exe_options = {
    "includes": [
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
        "sys",
        "threading"
    ]
}
# Caso precise incluir as DLLs do Visual C++ Redistributable
# include_msvcr = ['msvcp140.dll','vcruntime140.dll', 'vcruntime140_1.dll', 'vcruntime140_2.dll']

base = "Win32GUI" if sys.platform == "win32" else None

# Configuração da sua aplicação
setup(
    name="ExtratorPrescricoesHSF",  # Nome mais descritivo do aplicativo
    version="1.7.0",  # Versão do aplicativo (esquema major.minor.patch)
    description="Aplicativo para automatizar a extração e o download de prescrições médicas em formato PDF do sistema HSF.",  # Descrição detalhada
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", icon="icone.ico", base=base)]
)
