import cv2
from pyzbar.pyzbar import decode
from PIL import Image
import io
import hashlib

def extrair_url_qr_code(imagem_bytes):
    """
    Extrai a URL da NFC-e de um QR Code contido nos bytes de uma imagem.
    (Utiliza OpenCV e pyzbar)

    Args:
        imagem_bytes (bytes): Conteúdo binário da imagem (PNG ou JPG).

    Returns:
        str or None: A URL da NFC-e se encontrada, ou None.
    """
    try:
        img_pil = Image.open(io.BytesIO(imagem_bytes))
        
        img_np = np.array(img_pil.convert('RGB')) 
        img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        
        decoded_objects = decode(img_cv)

        if decoded_objects:
            qr_data = decoded_objects[0].data.decode('utf-8')
            if 'nfce' in qr_data.lower() and 'http' in qr_data.lower():
                return qr_data
            
        return None
    except Exception as e:
        return None

def extrair_hash_da_url(url_nfce):
    """
    Extrai um hash simples da URL da NFC-e para ser usado como identificador único.
    """
    try:
        if 'p=' in url_nfce:
            hash_qr = url_nfce.split('p=')[1].split('&')[0]
            return hash_qr
        
        return hashlib.sha256(url_nfce.encode('utf-8')).hexdigest()[:10]
        
    except Exception:
        return 'hash_desconhecido'