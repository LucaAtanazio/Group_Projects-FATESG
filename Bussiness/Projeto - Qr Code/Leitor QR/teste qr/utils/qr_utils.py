"""
Utilitários para extração e validação de Chaves de Acesso de cupons fiscais
"""

import re
import cv2
from typing import Optional, List, Tuple
from pyzbar.pyzbar import decode
import numpy as np

# Constantes
ACCESS_KEY_LENGTH = 44

def is_valid_access_key(key: str) -> bool:
    """
    Valida se uma string é uma chave de acesso válida
    
    Args:
        key: String a ser validada
        
    Returns:
        True se a chave é válida (44 dígitos numéricos)
    """
    if not key:
        return False
    
    # Deve ter exatamente 44 caracteres
    if len(key) != ACCESS_KEY_LENGTH:
        return False
    
    # Deve conter apenas dígitos
    if not key.isdigit():
        return False
    
    return True

def extract_access_key(data: str) -> Optional[str]:
    """
    Extrai a chave de acesso de 44 dígitos de uma string usando regex robusto
    
    Args:
        data: String contendo dados do QR Code
        
    Returns:
        Chave de acesso de 44 dígitos ou None se não encontrada
    """
    if not data:
        return None
    
    # Regex robusto para extrair 44 dígitos consecutivos
    match = re.search(r'(\d{44})', data)
    return match.group(1) if match else None

def find_all_access_keys(data: str) -> List[str]:
    """
    Encontra todas as chaves de acesso válidas em uma string
    
    Args:
        data: String contendo dados do QR Code
        
    Returns:
        Lista de chaves de acesso encontradas (pode estar vazia)
    """
    if not data:
        return []
    
    keys = []
    
    # Buscar todos os grupos de 44 dígitos
    pattern = r'\b(\d{44})\b'
    matches = re.finditer(pattern, data)
    
    for match in matches:
        key = match.group(1)
        if is_valid_access_key(key) and key not in keys:
            keys.append(key)
    
    # Se não encontrou com regex, tentar estratégias alternativas
    if not keys:
        key = extract_access_key(data)
        if key:
            keys.append(key)
    
    return keys

def decode_qr_from_image(image: np.ndarray) -> Tuple[List[str], List[Tuple[int, int, int, int]]]:
    """
    Decodifica QR codes de uma imagem e retorna dados + coordenadas
    
    Args:
        image: Imagem como numpy array (BGR ou RGB)
        
    Returns:
        Tupla contendo:
        - Lista de strings decodificadas dos QR codes encontrados
        - Lista de coordenadas (x, y, width, height) para cada QR code
    """
    try:
        # Decodificar QR codes
        decoded_objects = decode(image)
        
        # Extrair dados e coordenadas
        qr_data_list = []
        qr_coords_list = []
        
        for obj in decoded_objects:
            try:
                # Tentar decodificar como UTF-8
                data = obj.data.decode('utf-8')
                qr_data_list.append(data)
            except UnicodeDecodeError:
                # Fallback para latin-1
                try:
                    data = obj.data.decode('latin-1')
                    qr_data_list.append(data)
                except:
                    # Ignorar se não conseguir decodificar
                    continue
            
            rect = obj.rect
            qr_coords_list.append((rect.left, rect.top, rect.width, rect.height))
        
        return qr_data_list, qr_coords_list
    
    except Exception as e:
        print(f"Erro ao decodificar QR code: {e}")
        return [], []

def calculate_sharpness(image: np.ndarray) -> float:
    """
    Calcula a nitidez da imagem usando variância do Laplaciano
    
    Args:
        image: Imagem como numpy array (BGR ou grayscale)
        
    Returns:
        Valor de nitidez (quanto maior, mais nítida)
    """
    try:
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        variance = laplacian.var()
        
        return variance
    except Exception as e:
        print(f"Erro ao calcular nitidez: {e}")
        return 0.0

def apply_auto_focus_simulation(image: np.ndarray, sharpness_threshold: float = 100.0) -> np.ndarray:
    """
    Simula foco automático aplicando filtros de nitidez e contraste
    Aplica processamento apenas se a nitidez estiver abaixo do limiar
    
    Args:
        image: Imagem como numpy array (BGR)
        sharpness_threshold: Limiar de nitidez (padrão: 100.0)
        
    Returns:
        Imagem processada com melhor nitidez e contraste
    """
    try:
        # Calcular nitidez atual
        current_sharpness = calculate_sharpness(image)
        
        # Se a nitidez estiver boa, retornar imagem original
        if current_sharpness >= sharpness_threshold:
            return image
        
        # Aplicar suavização Gaussiana
        blurred = cv2.GaussianBlur(image, (5, 5), 0)
        
        # Converter para escala de cinza
        if len(blurred.shape) == 3:
            gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
        else:
            gray = blurred
        
        # Equalizar histograma para melhorar contraste
        equalized = cv2.equalizeHist(gray)
        
        # Converter de volta para BGR se necessário
        if len(image.shape) == 3:
            result = cv2.cvtColor(equalized, cv2.COLOR_GRAY2BGR)
        else:
            result = equalized
        
        return result
    
    except Exception as e:
        print(f"Erro ao aplicar auto-focus: {e}")
        return image

def enhance_qr_detection(image: np.ndarray) -> np.ndarray:
    """
    Aplica pré-processamento para melhorar detecção de QR codes
    
    Args:
        image: Imagem como numpy array (BGR)
        
    Returns:
        Imagem processada otimizada para leitura de QR codes
    """
    try:
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
        
        return denoised
    
    except Exception as e:
        print(f"Erro ao melhorar detecção: {e}")
        return image
