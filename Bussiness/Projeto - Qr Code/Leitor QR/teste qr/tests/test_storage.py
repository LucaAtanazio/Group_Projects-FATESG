"""
Testes para utils/storage.py
"""

import pytest
import os
import pandas as pd
from utils.storage import (
    initialize_csv,
    is_duplicate,
    save_receipt,
    get_all_receipts,
    CSV_FILE
)

@pytest.fixture
def clean_csv():
    """Fixture para limpar CSV antes e depois dos testes"""
    # Remover CSV se existir
    if os.path.exists(CSV_FILE):
        os.remove(CSV_FILE)
    
    yield
    
    # Limpar após teste
    if os.path.exists(CSV_FILE):
        os.remove(CSV_FILE)

class TestStorage:
    """Testes para persistência em CSV"""
    
    def test_initialize_csv(self, clean_csv):
        """Testa inicialização do CSV"""
        initialize_csv()
        assert os.path.exists(CSV_FILE)
        
        # Verificar cabeçalho
        df = pd.read_csv(CSV_FILE)
        expected_columns = ["timestamp_iso", "access_key", "raw_data", "source", "device_id", "image_saved"]
        assert list(df.columns) == expected_columns
    
    def test_save_receipt(self, clean_csv):
        """Testa salvamento de cupom"""
        key = "12345678901234567890123456789012345678901234"
        raw_data = "https://www.sefaz.rs.gov.br/NFCE/NFCE-COM.aspx?p=12345678901234567890123456789012345678901234"
        
        result = save_receipt(key, raw_data, source="camera")
        assert result is True
        
        # Verificar se foi salvo
        df = get_all_receipts()
        assert len(df) == 1
        assert df.iloc[0]['access_key'] == key
    
    def test_is_duplicate(self, clean_csv):
        """Testa detecção de duplicata"""
        key = "12345678901234567890123456789012345678901234"
        raw_data = "test data"
        
        # Primeiro salvamento
        assert is_duplicate(key) is False
        save_receipt(key, raw_data)
        
        # Segundo salvamento (duplicata)
        assert is_duplicate(key) is True
    
    def test_save_duplicate_returns_false(self, clean_csv):
        """Testa que salvar duplicata retorna False"""
        key = "12345678901234567890123456789012345678901234"
        raw_data = "test data"
        
        # Primeiro salvamento
        result1 = save_receipt(key, raw_data)
        assert result1 is True
        
        # Segundo salvamento (duplicata)
        result2 = save_receipt(key, raw_data)
        assert result2 is False
        
        # Verificar que só tem 1 registro
        df = get_all_receipts()
        assert len(df) == 1
    
    def test_get_all_receipts_empty(self, clean_csv):
        """Testa obter cupons quando CSV está vazio"""
        df = get_all_receipts()
        assert len(df) == 0
    
    def test_get_all_receipts_multiple(self, clean_csv):
        """Testa obter múltiplos cupons"""
        keys = [
            "11111111111111111111111111111111111111111111",
            "22222222222222222222222222222222222222222222",
            "33333333333333333333333333333333333333333333"
        ]
        
        for key in keys:
            save_receipt(key, f"data_{key}", source="upload")
        
        df = get_all_receipts()
        assert len(df) == 3
        assert all(key in df['access_key'].values for key in keys)
