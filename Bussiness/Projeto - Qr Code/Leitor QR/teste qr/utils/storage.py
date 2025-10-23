"""
Módulo de persistência de dados em CSV
"""

import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
import pandas as pd
import socket

# Constantes
CSV_FILE = "fiscal_receipts.csv"
CSV_COLUMNS = [
    "access_key",
    "timestamp",
    "source"
]

def get_device_id() -> str:
    """Retorna um identificador único do dispositivo"""
    try:
        return socket.gethostname()
    except:
        return "unknown"

def initialize_csv():
    """Inicializa o arquivo CSV se não existir"""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()

def is_duplicate(access_key: str) -> bool:
    """
    Verifica se a chave de acesso já existe no CSV
    
    Args:
        access_key: Chave de acesso a verificar
        
    Returns:
        True se já existe, False caso contrário
    """
    initialize_csv()
    
    try:
        df = pd.read_csv(CSV_FILE)
        if 'access_key' not in df.columns:
            return False
        return access_key in df['access_key'].values
    except Exception as e:
        print(f"Erro ao verificar duplicata: {e}")
        return False

def save_receipt(access_key: str, raw_data: str, source: str = "camera") -> bool:
    initialize_csv()
    try:
        if is_duplicate(access_key):
            return False

        df = pd.read_csv(CSV_FILE)
        new_row = pd.DataFrame([{
            "access_key": access_key,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "source": source
        }])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(CSV_FILE, index=False, encoding='utf-8')
        return True
    except Exception as e:
        print(f"Erro ao salvar cupom: {e}")
        return False

def get_all_receipts() -> pd.DataFrame:
    """
    Retorna todos os cupons salvos como DataFrame
    
    Returns:
        DataFrame com todos os cupons
    """
    initialize_csv()
    
    try:
        df = pd.read_csv(CSV_FILE)
        return df
    
    except Exception as e:
        print(f"Erro ao ler cupons: {e}")
        return pd.DataFrame(columns=CSV_COLUMNS)

def get_receipt_count() -> int:
    """Retorna o número total de cupons salvos"""
    df = get_all_receipts()
    return len(df)
