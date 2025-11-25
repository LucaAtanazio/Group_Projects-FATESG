import pandas as pd
import os

COLUNAS_ITENS = [
    'data_venda', 'hora_venda', 'forma_pagamento', 
    'produto', 'quantidade', 'preco_unitario', 'total_item', 
    'valor_total_nota', 'hash_qr'
]
COLUNAS_NOTAS = [
    'data_venda', 'hora_venda', 'forma_pagamento', 
    'valor_total', 'hash_qr'
]

PASTA_DADOS = 'data'
ARQUIVO_ITENS = os.path.join(PASTA_DADOS, 'itens_nfce.csv')
ARQUIVO_NOTAS = os.path.join(PASTA_DADOS, 'notas_nfce.csv')

def garantir_diretorio():
    """Cria a pasta 'data' se ela não existir."""
    os.makedirs(PASTA_DADOS, exist_ok=True)

def salvar_dados_em_csv(dados_nota, lista_itens, hash_qr):
    """
    Salva os dados de uma única NFC-e nos arquivos CSV de notas e itens.
    
    Args:
        dados_nota (dict): Dicionário com dados gerais da nota.
        lista_itens (list): Lista de dicionários com dados dos produtos.
        hash_qr (str): Hash único da nota.
    """
    garantir_diretorio()
    
    if dados_nota:
        dados_nota['hash_qr'] = hash_qr
        
    if lista_itens:
        for item in lista_itens:
            item['hash_qr'] = hash_qr
            
        df_itens = pd.DataFrame(lista_itens, columns=COLUNAS_ITENS)
        salvar_anexando(df_itens, ARQUIVO_ITENS)

    if dados_nota:
        df_notas = pd.DataFrame([dados_nota], columns=COLUNAS_NOTAS)
        salvar_anexando(df_notas, ARQUIVO_NOTAS)

def salvar_anexando(df, nome_arquivo):
    """Anexa um DataFrame a um arquivo CSV existente ou cria um novo."""
    try:
        incluir_header = not os.path.exists(nome_arquivo)
        
        df.to_csv(nome_arquivo, mode='a', header=incluir_header, index=False, sep=';', encoding='utf-8')
        print(f"Dados salvos com sucesso em: {nome_arquivo}")
        
    except Exception as e:
        print(f"Erro ao salvar dados no CSV {nome_arquivo}: {e}")