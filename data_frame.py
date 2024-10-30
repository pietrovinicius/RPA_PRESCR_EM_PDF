import os
import PyPDF2
import pandas as pd 


#TODO: funcao para pegar planilha gerada e montar o data frame:

def pdf_para_csv():
    texto_completo = ""
    
    #acessando pasta download:
    print("get_latest_xls_from_downloads")
    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
    print(f'Caminho da pasta download: {downloads_path}')
    
    #verificando arquivos da pasta download
    files = [f for f in os.listdir(downloads_path) if f.endswith('.pdf')]
    print(f"Arquivos:\n{files}")

    #ultimo arquivo
    ultimo_arquivo = os.path.join(downloads_path, files[0])
    print(f"\n*****Ultimo arquivo: {ultimo_arquivo}")
    
    with open(ultimo_arquivo, 'rb') as arquivo_pdf: 
        leitor_pdf = PyPDF2.PdfReader(arquivo_pdf) 
        
        # Ler todas as páginas do PDF 
        for pagina in range(len(leitor_pdf.pages)): 
            pagina_atual = leitor_pdf.pages[pagina] 
            texto = pagina_atual.extract_text() 
            texto_completo += texto + "\n"
            #print(texto_completo)
            
        linhas = texto_completo.split('\n') 
        dados = [linha.split() for linha in linhas if linha.strip()] 
        df = pd.DataFrame(dados) 
        
        #exibindo as 5 primeiras linhas:
        print(df.head(5))
        
        #exibindo todas as linhas mas só a primeira coluna:
        print(df.iloc[:, 0].to_string(index=False))
        
        #retirando linhas com NR_ATEND
        df_filtered = df[df.iloc[:, 0] != 'NR_ATEND']
        print(df_filtered.iloc[:, 0].to_string(index=False))
    return df_filtered.iloc[:, 0].to_string(index=False)
        
if __name__ == "__main__":
    try:
        print(f"\n\n=======================================================================================")
        #get_latest_xls_from_downloads()
        
        print(pdf_para_csv())
        #criar_dataframe_do_texto(pdf_para_csv())
        

    except Exception as erro:
        print(f"================================ Error: \n{erro}")         