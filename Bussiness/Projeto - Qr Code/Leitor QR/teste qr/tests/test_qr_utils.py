"""
Testes unitários para utils/qr_utils.py
"""

import pytest
from utils.qr_utils import (
    is_valid_access_key,
    extract_access_key,
    find_all_access_keys
)

class TestIsValidAccessKey:
    """Testes para validação de chave de acesso"""
    
    def test_valid_key(self):
        """Testa chave válida de 44 dígitos"""
        key = "12345678901234567890123456789012345678901234"
        assert is_valid_access_key(key) is True
    
    def test_invalid_length_short(self):
        """Testa chave com menos de 44 dígitos"""
        key = "123456789012345678901234567890"
        assert is_valid_access_key(key) is False
    
    def test_invalid_length_long(self):
        """Testa chave com mais de 44 dígitos"""
        key = "123456789012345678901234567890123456789012345"
        assert is_valid_access_key(key) is False
    
    def test_invalid_non_numeric(self):
        """Testa chave com caracteres não numéricos"""
        key = "1234567890123456789012345678901234567890123A"
        assert is_valid_access_key(key) is False
    
    def test_empty_string(self):
        """Testa string vazia"""
        assert is_valid_access_key("") is False
    
    def test_none_value(self):
        """Testa valor None"""
        assert is_valid_access_key(None) is False

class TestExtractAccessKey:
    """Testes para extração de chave de acesso"""
    
    def test_extract_from_pure_digits(self):
        """Testa extração de 44 dígitos puros"""
        data = "12345678901234567890123456789012345678901234"
        result = extract_access_key(data)
        assert result == "12345678901234567890123456789012345678901234"
    
    def test_extract_from_url_parameter_p(self):
        """Testa extração de URL com parâmetro p="""
        data = "https://www.sefaz.rs.gov.br/NFCE/NFCE-COM.aspx?p=43210987654321098765432109876543210987654321"
        result = extract_access_key(data)
        assert result == "43210987654321098765432109876543210987654321"
    
    def test_extract_from_url_parameter_chnfe(self):
        """Testa extração de URL com parâmetro chNFe="""
        data = "http://nfe.fazenda.gov.br/portal/consultaRecaptcha.aspx?chNFe=35210123456789012345678901234567890123456789"
        result = extract_access_key(data)
        assert result == "35210123456789012345678901234567890123456789"
    
    def test_extract_with_multiple_parameters(self):
        """Testa extração de URL com múltiplos parâmetros"""
        data = "https://www.sefaz.rs.gov.br/NFCE/NFCE-COM.aspx?p=43210987654321098765432109876543210987654321|2|1|1|ABC123"
        result = extract_access_key(data)
        assert result == "43210987654321098765432109876543210987654321"
    
    def test_extract_from_text_with_key(self):
        """Testa extração de texto contendo chave"""
        data = "Chave de Acesso: 12345678901234567890123456789012345678901234 - Consulte em www.sefaz.gov.br"
        result = extract_access_key(data)
        assert result == "12345678901234567890123456789012345678901234"
    
    def test_no_valid_key(self):
        """Testa quando não há chave válida"""
        data = "Texto sem chave de acesso válida 123456"
        result = extract_access_key(data)
        assert result is None
    
    def test_empty_string(self):
        """Testa string vazia"""
        result = extract_access_key("")
        assert result is None
    
    def test_none_value(self):
        """Testa valor None"""
        result = extract_access_key(None)
        assert result is None
    
    def test_multiple_digit_sequences(self):
        """Testa múltiplas sequências de dígitos, escolhe a de 44"""
        data = "123456 78901234567890 12345678901234567890123456789012345678901234 999"
        result = extract_access_key(data)
        assert result == "12345678901234567890123456789012345678901234"

class TestFindAllAccessKeys:
    """Testes para encontrar todas as chaves de acesso"""
    
    def test_find_single_key(self):
        """Testa encontrar uma única chave"""
        data = "Chave: 12345678901234567890123456789012345678901234"
        result = find_all_access_keys(data)
        assert len(result) == 1
        assert result[0] == "12345678901234567890123456789012345678901234"
    
    def test_find_multiple_keys(self):
        """Testa encontrar múltiplas chaves"""
        data = "Chave1: 11111111111111111111111111111111111111111111 Chave2: 22222222222222222222222222222222222222222222"
        result = find_all_access_keys(data)
        assert len(result) == 2
        assert "11111111111111111111111111111111111111111111" in result
        assert "22222222222222222222222222222222222222222222" in result
    
    def test_find_no_keys(self):
        """Testa quando não há chaves"""
        data = "Texto sem chaves válidas"
        result = find_all_access_keys(data)
        assert len(result) == 0
    
    def test_find_duplicate_keys(self):
        """Testa que não retorna chaves duplicadas"""
        data = "Chave: 12345678901234567890123456789012345678901234 Repetida: 12345678901234567890123456789012345678901234"
        result = find_all_access_keys(data)
        assert len(result) == 1
