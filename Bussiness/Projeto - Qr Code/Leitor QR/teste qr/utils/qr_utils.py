import re
import cv2
from typing import Optional, List, Tuple
from pyzbar.pyzbar import decode as pyzbar_decode
import numpy as np
import time

# =======================
# 🔹 Constantes
# =======================
ACCESS_KEY_LENGTH = 44
SEFAZ_GO_URL_PREFIX = "https://nfeweb.sefaz.go.gov.br/nfeweb/sites/nfce/danfeNFCe?p="


# =======================
# 🔹 Validação e extração
# =======================
def is_valid_access_key(key: str) -> bool:
    """Valida se uma string é uma chave de acesso fiscal válida (44 dígitos numéricos)."""
    return bool(key and key.isdigit() and len(key) == ACCESS_KEY_LENGTH)


def extract_access_key(data: str) -> Optional[str]:
    """
    Extrai a chave de acesso de QR Code fiscal da SEFAZ-GO e valida formato.
    Exemplo de URL esperada:
    https://nfeweb.sefaz.go.gov.br/nfeweb/sites/nfce/danfeNFCe?p=52250339346861034147651070004999491107141815|...
    """
    if not data:
        return None

    # Aceita variações válidas de URL da SEFAZ-GO
    valid_prefixes = [
    "https://nfeweb.sefaz.go.gov.br/nfeweb/sites/nfce/danfeNFCe?p=",
    "http://nfeweb.sefaz.go.gov.br/nfeweb/sites/nfce/danfeNFCe?p=",
    "https://nfe.sefaz.go.gov.br/nfeweb/sites/nfce/danfeNFCe?p=",
    "http://nfe.sefaz.go.gov.br/nfeweb/sites/nfce/danfeNFCe?p="
]

    if not any(data.startswith(prefix) for prefix in valid_prefixes):
        print(f"[v0] QR não reconhecido como SEFAZ-GO: {data[:80]}")
        return None


    match = re.search(r"p=(\d{44})", data)
    if match:
        key = match.group(1)
        if is_valid_access_key(key):
            print(f"[v0] ✅ Chave SEFAZ-GO extraída: {key}")
            return key
        else:
            print(f"[v0] ❌ Chave inválida detectada no QR.")
    else:
        print(f"[v0] ⚠️ Nenhuma chave de 44 dígitos encontrada no QR da SEFAZ-GO.")
    return None


def find_all_access_keys(data: str) -> List[str]:
    """Procura múltiplas chaves válidas de 44 dígitos em uma string."""
    if not data:
        return []

    found = list(set(re.findall(r"\b\d{44}\b", data)))
    return [k for k in found if is_valid_access_key(k)]


# =======================
# 🔹 Métricas e cálculos
# =======================
def calculate_sharpness(image: np.ndarray) -> float:
    """Calcula nitidez da imagem (variância do Laplaciano)."""
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        return cv2.Laplacian(gray, cv2.CV_64F).var()
    except Exception as e:
        print(f"[v0] Erro em calculate_sharpness: {e}")
        return 0.0


def calculate_brightness(image: np.ndarray) -> float:
    """Calcula brilho médio da imagem (0 a 255)."""
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        return float(np.mean(gray))
    except Exception as e:
        print(f"[v0] Erro ao calcular brilho: {e}")
        return 128.0


# =======================
# 🔹 Filtros e pré-processamento
# =======================
def apply_auto_focus_simulation(image: np.ndarray, sharpness_threshold: float = 100.0) -> np.ndarray:
    """Simula foco automático aplicando nitidez e contraste se a imagem estiver desfocada."""
    try:
        if calculate_sharpness(image) >= sharpness_threshold:
            return image

        blurred = cv2.GaussianBlur(image, (5, 5), 0)
        gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY) if len(blurred.shape) == 3 else blurred
        equalized = cv2.equalizeHist(gray)
        return cv2.cvtColor(equalized, cv2.COLOR_GRAY2BGR) if len(image.shape) == 3 else equalized
    except Exception as e:
        print(f"[v0] Erro em auto_focus: {e}")
        return image


def preprocess_image_for_qr(image: np.ndarray) -> np.ndarray:
    """Aplica pré-processamento avançado para melhorar leitura de QR em fotos de notas."""
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image

        # Equalização global + filtro bilateral
        gray = cv2.equalizeHist(gray)
        gray = cv2.bilateralFilter(gray, 9, 75, 75)

        # CLAHE (contraste local)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)

        # Threshold adaptativo (binário)
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 11, 2)
        return thresh
    except Exception as e:
        print(f"[v0] Erro em preprocess_image_for_qr: {e}")
        return image


def balance_white_and_color(image: np.ndarray) -> np.ndarray:
    """Corrige coloração amarelada típica de notas fiscais."""
    try:
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl, a, b))
        return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    except Exception:
        return image


# =======================
# 🔹 Leitura de QR Codes
# =======================
def decode_qr_from_image(image: np.ndarray) -> Tuple[List[str], List[Tuple[int, int, int, int]]]:
    """Decodifica QR codes usando pyzbar."""
    qr_data_list, qr_coords_list = [], []
    try:
        decoded = pyzbar_decode(image)
        for obj in decoded:
            try:
                data = obj.data.decode("utf-8")
            except UnicodeDecodeError:
                data = obj.data.decode("latin-1", errors="ignore")
            qr_data_list.append(data)
            (x, y, w, h) = obj.rect
            qr_coords_list.append((x, y, w, h))
    except Exception as e:
        print(f"[v0] Erro ao decodificar pyzbar: {e}")
    return qr_data_list, qr_coords_list


def decode_qr_with_multiple_attempts(image: np.ndarray) -> Tuple[List[str], List[Tuple[int, int, int, int]], dict]:
    """
    Tenta decodificar QR codes com múltiplas abordagens mais robustas:
      - Variações de contraste e equalização
      - Threshold adaptativo e rotação
      - Fallback entre pyzbar e cv2.QRCodeDetector
    Retorna (lista_dados, lista_coordenadas, métricas)
    """
    start = time.time()
    attempts = 0
    qr_data_list, qr_coords_list = [], []
    method_used = None

    # =============================
    # Pré-processamentos principais
    # =============================
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    variants = [
        ("original", gray),
        ("equalized", cv2.equalizeHist(gray)),
        ("contrast", cv2.convertScaleAbs(gray, alpha=1.5, beta=0)),
        ("adaptive", cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                           cv2.THRESH_BINARY, 31, 8)),
        ("blur", cv2.medianBlur(gray, 3))
    ]

    # Rotação leve (corrige QR torto)
    rotation_angles = [0, 5, -5, 10, -10]

    # =============================
    # Loop de tentativas
    # =============================
    for name, variant in variants:
        for ang in rotation_angles:
            attempts += 1
            if attempts > 12:  # limite de tentativas
                break

            # Rotacionar se necessário
            if ang != 0:
                (h, w) = variant.shape[:2]
                M = cv2.getRotationMatrix2D((w // 2, h // 2), ang, 1.0)
                rotated = cv2.warpAffine(variant, M, (w, h))
            else:
                rotated = variant

            # 🔹 1) pyzbar
            try:
                decoded = pyzbar_decode(rotated)
                if decoded:
                    for obj in decoded:
                        try:
                            data = obj.data.decode("utf-8")
                        except UnicodeDecodeError:
                            data = obj.data.decode("latin-1", errors="ignore")
                        qr_data_list.append(data)
                        (x, y, w, h) = obj.rect
                        qr_coords_list.append((x, y, w, h))
                    method_used = f"pyzbar_{name}_rot{ang}"
                    raise StopIteration
            except StopIteration:
                break
            except Exception as e:
                print(f"[v1] Erro pyzbar_{name}_rot{ang}: {e}")

            # 🔹 2) Fallback: OpenCV
            try:
                detector = cv2.QRCodeDetector()
                val, points, _ = detector.detectAndDecode(rotated)
                if val:
                    qr_data_list = [val]
                    if points is not None and len(points) > 0:
                        pts = points[0]
                        x, y, w, h = cv2.boundingRect(pts)
                        qr_coords_list = [(x, y, w, h)]
                    else:
                        qr_coords_list = [(0, 0, rotated.shape[1], rotated.shape[0])]
                    method_used = f"cv2_{name}_rot{ang}"
                    raise StopIteration
            except StopIteration:
                break
            except Exception as e:
                print(f"[v1] Erro cv2_{name}_rot{ang}: {e}")

        if qr_data_list:
            break

    # =============================
    # Estatísticas
    # =============================
    total_time = time.time() - start
    print(f"[v1] ⏱️ {attempts} tentativas | Método: {method_used or 'falha'} | Tempo: {total_time:.2f}s")

    stats = {
        "attempts": attempts,
        "processing_time": total_time,
        "method_used": method_used or "none"
    }

    return qr_data_list, qr_coords_list, stats

def try_opencv_qr(gray_image: np.ndarray) -> List[str]:
    """Fallback simples usando apenas o detector nativo do OpenCV."""
    try:
        detector = cv2.QRCodeDetector()
        data, points, _ = detector.detectAndDecode(gray_image)
        if data:
            return [data]
    except Exception as e:
        print(f"[v1] Erro try_opencv_qr: {e}")
    return []
