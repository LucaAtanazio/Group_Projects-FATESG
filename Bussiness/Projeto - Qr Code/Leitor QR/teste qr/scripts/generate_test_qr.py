"""
Script para gerar imagens de QR codes para testes
"""

import qrcode
from pathlib import Path

# Criar diretório de fixtures
fixtures_dir = Path("tests/fixtures")
fixtures_dir.mkdir(exist_ok=True)

# Casos de teste
test_cases = {
    "qr_pure_digits.png": "12345678901234567890123456789012345678901234",
    
    "qr_url_sefaz.png": "https://www.sefaz.rs.gov.br/NFCE/NFCE-COM.aspx?p=43210987654321098765432109876543210987654321",
    
    "qr_url_multiple_params.png": "https://www.sefaz.rs.gov.br/NFCE/NFCE-COM.aspx?p=35210123456789012345678901234567890123456789|2|1|1|ABC123DEF456",
    
    "qr_url_chnfe.png": "http://nfe.fazenda.gov.br/portal/consultaRecaptcha.aspx?chNFe=52210999888777666555444333222111000999888777",
    
    "qr_invalid_short.png": "123456789012345678901234567890",  # Menos de 44 dígitos
    
    "qr_text_with_key.png": "Nota Fiscal Eletrônica - Chave de Acesso: 11223344556677889900112233445566778899001122 - Consulte em www.sefaz.gov.br"
}

print("Gerando imagens de QR codes para testes...\n")

for filename, data in test_cases.items():
    # Criar QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    # Gerar imagem
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Salvar
    filepath = fixtures_dir / filename
    img.save(filepath)
    
    print(f"✓ {filename}")
    print(f"  Dados: {data[:80]}{'...' if len(data) > 80 else ''}\n")

print(f"\n✅ {len(test_cases)} imagens geradas em {fixtures_dir}/")
