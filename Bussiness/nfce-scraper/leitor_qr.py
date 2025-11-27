# leitor_qr.py

import os
from io import BytesIO
from PIL import Image
from pyzbar.pyzbar import decode as pyzbar_decode
import numpy as np

# --- Funções de Extração da URL (Núcleo do Fiscalizador) ---

def extrair_chaves_da_url(url_completa: str) -> tuple[str, str] | tuple[None, None]:
    """
    Processa a URL completa do QR Code (formato: ...p=CHAVE|VERSAO|TIPO|ID|TOKEN)
    e extrai a Chave de Acesso de 44 dígitos e o Token de Segurança.
    """
    
    # URL de exemplo (apenas para referência da lógica):
    # http://nfe.sefaz.go.gov.br/nfeweb/sites/nfce/danfeNFCe?p=522503...07141815|2|1|1|DF46C0CAD...8E215

    if not url_completa or '?p=' not in url_completa:
        return None, None
    
    try:
        # 1. Isola o payload (o que vem depois de '?p=')
        payload_bruto = url_completa.split('?p=')[-1]
        
        # 2. Divide a string pelo separador '|'
        componentes = payload_bruto.split('|')
        
        # O formato da NFC-e deve ter no mínimo 5 componentes.
        if len(componentes) < 5:
            return None, None
            
        # A chave de acesso é o primeiro componente
        chave_acesso = componentes[0].strip()
        
        # O token é o último componente (índice 4 ou mais, dependendo do estado)
        # Vamos pegar o último componente para maior robustez, pois alguns estados adicionam campos.
        token_seguranca = componentes[-1].strip()
        
        # Validação simples do formato (Chave de Acesso deve ter 44 dígitos)
        if len(chave_acesso) != 44 or not chave_acesso.isdigit():
             return None, None
        
        return chave_acesso, token_seguranca
        
    except Exception:
        # Erros como index out of range (se o payload for malformado)
        return None, None

def extrair_hash_da_url(url_completa: str) -> str | None:
    """
    Retorna o hash de controle (Chave de Acesso de 44 dígitos) para o Fiscalizador.
    """
    chave_acesso, _ = extrair_chaves_da_url(url_completa)
    # A Chave de Acesso é o nosso hash_qr único de controle
    return chave_acesso

# --- Função de Decodificação de Imagem (Para o Upload do Streamlit) ---

def extrair_url_qr_code(image_bytes: bytes) -> str | None:
    """
    Decodifica o QR Code contido na imagem binária.
    
    Args:
        image_bytes: O conteúdo binário da imagem (passado pelo st.file_uploader.read()).
        
    Returns:
        A URL do QR Code decodificado, ou None se não for encontrado.
    """
    try:
        # Abre a imagem a partir dos bytes
        image = Image.open(BytesIO(image_bytes)).convert('RGB')
        
        # Converte para array numpy
        img_np = np.array(image)
        
        # Decodifica o QR Code
        decoded_objects = pyzbar_decode(img_np)
        
        if decoded_objects:
            # Assume que o primeiro QR Code encontrado é o da NFC-e
            qr_data = decoded_objects[0].data.decode('utf-8')
            return qr_data
        
        return None
        
    except Exception:
        # print(f"Erro ao decodificar QR Code da imagem: {e}")
        return None


if __name__ == '__main__':
    # --- Demonstração de Teste ---
    print("--- Teste do Módulo leitor_qr.py ---")
    
    # URL de Exemplo Válida
    url_valida = "http://nfe.sefaz.go.gov.br/nfeweb/sites/nfce/danfeNFCe?p=52250339346861034147651070004999491107141815|2|1|1|DF46C0CAD32EF01BE6B47848D0D7BD145878E215"
    chave_valida, token_valido = extrair_chaves_da_url(url_valida)
    hash_valido = extrair_hash_da_url(url_valida)
    
    print("\n[SUCESSO] URL Válida:")
    print(f"Chave de Acesso (44D): {chave_valida}")
    print(f"Token de Segurança:    {token_valido}")
    print(f"Hash de Controle (App): {hash_valido}")
    
    # URL de Exemplo Inválida (faltando o payload)
    url_invalida = "http://nfe.sefaz.go.gov.br/nfeweb/sites/nfce/danfeNFCe?chave=123"
    chave_invalida, token_invalido = extrair_chaves_da_url(url_invalida)
    
    print("\n[FALHA ESPERADA] URL Inválida:")
    print(f"Chave de Acesso (44D): {chave_invalida}")
    print(f"Token de Segurança:    {token_invalido}")