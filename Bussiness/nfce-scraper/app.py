import streamlit as st
from leitor_qr import extrair_url_qr_code, extrair_hash_da_url
from scraper_nfce import raspar_dados_nfce
from salvador_csv import salvar_dados_em_csv
import os

# --- Configuração da Página Streamlit ---
st.set_page_config(
    page_title="NFC-e Scraper",
    layout="centered"
)

def processar_nfce(url_nfce):
    """Função principal que orquestra a extração e o salvamento."""
    if not url_nfce:
        st.error(" URL/código da NFC-e inválido.")
        return

    # 1. Extrair Hash
    hash_qr = extrair_hash_da_url(url_nfce)
    
    st.info(f"🔎 Iniciando scraping da NFC-e com Hash: **{hash_qr}**")
    
    # 2. Scraping dos Dados
    with st.spinner('🌐 Acessando e renderizando a página da Sefaz (via Selenium Headless)...'):
        dados_nota, lista_itens = raspar_dados_nfce(url_nfce)
        
    # 3. Verificação e Salvamento
    if dados_nota and lista_itens:
        
        st.success("✅ Dados da NFC-e extraídos com sucesso!")
        st.write(f"**Valor Total:** R$ {dados_nota.get('valor_total'):.2f}")
        st.write(f"**Itens Encontrados:** {len(lista_itens)}")
        
        with st.spinner('Salvando dados em CSV...'):
            salvar_dados_em_csv(dados_nota, lista_itens, hash_qr)
        
        st.success(f"**Dados salvos com sucesso** nos arquivos CSV dentro da pasta /{salvador_csv.PASTA_DADOS}/")
        
    else:
        st.error(f" Falha ao extrair dados da NFC-e: {url_nfce}. Verifique o log do terminal.")


# --- Interface Streamlit ---

st.title("📄 NFC-e Scraper Simples")

st.markdown("""
Esta ferramenta extrai dados de Notas Fiscais de Consumidor Eletrônica (NFC-e) 
através do QR Code ou URL/código manual e salva tudo em arquivos CSV.
""")

# --- Opção 1: Upload de Imagem QR Code ---
st.header("1. Upload de Imagem do QR Code")

uploaded_file = st.file_uploader(
    "Selecione uma imagem (PNG/JPG) contendo o QR Code da NFC-e",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    st.image(uploaded_file, caption='Imagem Carregada', width=150)
    
    url_nfce_qr = extrair_url_qr_code(uploaded_file.read())
    
    if url_nfce_qr:
        st.info(f"URL extraída do QR Code: \n\n`{url_nfce_qr}`")
        if st.button("🚀 Processar NFC-e (QR Code)"):
            processar_nfce(url_nfce_qr)
    else:
        st.warning("⚠️ Não foi possível extrair uma URL de NFC-e válida do QR Code.")

st.markdown("---")

# --- Opção 2: Entrada Manual (URL ou Código) ---
st.header("2. Entrada Manual da URL/Código da NFC-e")

url_manual = st.text_area(
    "Cole aqui a URL completa da NFC-e ou a string do QR Code:",
    height=100,
    key='url_manual_input'
)

if url_manual:
    if url_manual.lower().startswith('http') and 'nfce' in url_manual.lower():
        if st.button("🚀 Processar NFC-e (Manual)"):
            processar_nfce(url_manual)
    else:
        st.warning("⚠️ O texto inserido não parece ser uma URL válida de NFC-e (deve começar com 'http' e conter 'nfce').")