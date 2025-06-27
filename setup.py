"""
10/01/2025
@PLima

Automação PDD - Setup.py para criação do executável (.exe)

Para gerar o executável do seu aplicativo com cx_Freeze, você já tem o arquivo setup.py configurado corretamente, 
o que é um ótimo começo!

1) Navegue até o diretório do seu projeto: 
Abra o terminal (Prompt de Comando no Windows, ou PowerShell) 
e use o comando:

cd c:\Pietro\Projetos\RPA_PRESCR_EM_PDF

2) Execute o comando:

python setup.py build

3)Aguarde a conclusão: O cx_Freeze vai analisar seu main.py, identificar as dependências, coletar os arquivos especificados no includefiles do setup.py (como config.ini, HSF_LOGO_-_60x77_001.png, instantclient-basiclite-windows.x64-23.6.0.24.10\instantclient_23_6, btn_manter.png, icone.ico) e empacotar tudo. Isso pode levar alguns minutos, dependendo do tamanho do seu projeto e do número de dependências.

4) Localize o executável: Após a execução bem-sucedida, o cx_Freeze criará uma nova pasta chamada build no diretório do seu projeto. Dentro dela, haverá outra pasta (cujo nome dependerá do seu sistema operacional e versão do Python, algo como exe.win-amd64-3.x). O executável ExtratorPrescricoesHSF.exe estará dentro dessa subpasta.

O caminho final será algo parecido com: c:\Pietro\Projetos\RPA_PRESCR_EM_PDF\build\exe.win-amd64-3.x\ExtratorPrescricoesHSF.exe

"""

import sys
from cx_Freeze import setup, Executable

# Lista de arquivos/pastas que devem ser incluídos no pacote .exe
includefiles = ["HSF_LOGO_-_60x77_001.png", '.', 'instantclient-basiclite-windows.x64-23.6.0.24.10\instantclient_23_6', 'btn_manter.png', 'icone.ico', 'config.ini']

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
    version="1.9.1",  # Versão do aplicativo (esquema major.minor.patch)
    description="Aplicativo para automatizar a extração e o download de prescrições médicas em formato PDF do sistema HSF.",  # Descrição detalhada
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", icon="icone.ico", base=base)]
)
