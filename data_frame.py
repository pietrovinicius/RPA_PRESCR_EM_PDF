import os
import pandas as pd


#TODO: funcao para pegar planilha gerada e montar o data frame:
def get_latest_xls_from_downloads():
    try:
        # Usando a função de deletar todos os arquivos:
        
        #delete_path = os.path.join(os.path.expanduser("~"), "Downloads")
        #print(f"delete_path:{delete_path}")
        #delete_all_files_in_directory(delete_path)
        #print("delete_all_files_in_directory(delete_path)")
        
        #acessando pasta download:
        print("get_latest_xls_from_downloads")
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        print(f'Caminho da pasta download: {downloads_path}')
        
        #verificando arquivos da pasta download
        files = [f for f in os.listdir(downloads_path) if f.endswith('.xlsx')]
        print(f"Files:\n{files}")
    
        #ultimo arquivo
        ultimo_arquivo = os.path.join(downloads_path, files[0])
        print(f"\n\n*****Ultimo arquivo: {ultimo_arquivo}")
        
        df = pd.read_excel(ultimo_arquivo)
        print(f"\nDF:\n{df.head()}\n")
        #
        ##files.sort(key=lambda x: os.path.getmtime(os.path.join(downloads_path, x)), reverse=True)
        #
        #if not files:
        #    print("\n\nif not files")
        #    return None
        
        #ultimo_arquivo = os.path.join(downloads_path, files[0])
        
        #df = pd.read_excel(ultimo_arquivo)
        #print(f"\nDF:\n{df}\n")
        
        #return df
    except Exception as erro:
        print(f"\nget_latest_xls_from_downloads ================================ Error: \n{erro}")
        
        
if __name__ == "__main__":
    try:
        print(f"\n\n=======================================================================================")
        get_latest_xls_from_downloads()

    except Exception as erro:
        print(f"================================ Error: \n{erro}")         