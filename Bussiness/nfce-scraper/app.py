# app.py

import streamlit as st
import os

# Importações dos módulos do projeto (Você deve garantir que esses arquivos estejam disponíveis)
try:
    # A IDEIA É QUE VOCÊ SUBSTITUA ESTES ARQUIVOS PELOS SEUS VERSÃO NFC-e SCRAPING
    from leitor_qr import extrair_url_qr_code, extrair_hash_da_url
    from scraper_nfce import raspar_dados_nfce
    from salvador_csv import salvar_dados_em_csv, PASTA_DADOS
except ImportError as e:
    st.error(f"Erro ao carregar módulos: {e}. Verifique se os arquivos leitor_qr.py, scraper_nfce.py e salvador_csv.py estão no diretório correto.")
    # Define valores padrão para evitar que o Streamlit quebre completamente se houver erro
    def extrair_url_qr_code(*args): return None
    def extrair_hash_da_url(*args): return 'erro_hash'
    def raspar_dados_nfce(*args): return None, None
    def salvar_dados_em_csv(*args): pass
    PASTA_DADOS = 'data'


# --- Configuração e Estilo do Fiscalizador ---
st.set_page_config(
    page_title="O Fiscalizador - Controle de Compras",
    page_icon="🔎", # Ícone de lupa
    layout="centered"
)

# BLOCO DE ESTILO (Ajustado para Fundo CLARO e sintaxe limpa)
st.markdown("""
<style>
    /* 1. Títulos: Mudam para AZUL ESCURO para contraste */
    h1, h2, h3 {
        color: #003366 !important; /* Azul Escuro */
    }
    
    /* 2. Cores de Status: Mantêm a visibilidade no fundo claro */
    .status-reading {
        background-color: #e3f2fd; /* Fundo mais claro para leitura */
        color: #1565C0; /* Texto azul escuro */
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #1565C0;
        margin: 10px 0;
    }
    .status-success {
        background-color: #e8f5e9; /* Fundo verde pastel */
        color: #2e7d32; /* Texto verde escuro */
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #2e7d32;
        margin: 10px 0;
    }
    .status-error {
        background-color: #ffebee; /* Fundo vermelho pastel */
        color: #c62828; /* Texto vermelho escuro */
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #c62828;
        margin: 10px 0;
    }
    .recent-read {
        background-color: #ffffff; /* Fundo branco para sidebar */
        color: #333333; /* Texto escuro */
        padding: 10px;
        border-radius: 8px;
        margin: 8px 0;
        border-left: 3px solid #0077B6; /* Barra azul */
    }
</style>
""", unsafe_allow_html=True)


# --- Função Principal de Processamento (O Orquestrador do Fiscalizador) ---
def processar_nfce(url_nfce):
    """Função que orquestra a extração e o salvamento."""
    st.markdown("---")
    
    if not url_nfce:
        st.markdown('<div class="status-error">❌ ERRO DO FISCALIZADOR: URL/Código de NFC-e não fornecido. Não podemos controlar o que não vemos.</div>', unsafe_allow_html=True)
        return

    # --- Passo 1: Extrair Hash de Controle ---
    # CORREÇÃO do NameError: Usa o parâmetro de entrada 'url_nfce'
    hash_qr = extrair_hash_da_url(url_nfce)
    
    if not hash_qr:
        st.markdown(f'<div class="status-error">❌ ERRO: Não foi possível extrair a Chave de Acesso da URL. Verifique o formato do link.</div>', unsafe_allow_html=True)
        return

    st.info(f"🔎 FISCALIZANDO NOTA: Chave de Controle **{hash_qr}** sendo processada...") 
    
    # 2. Scraping dos Dados (O Braço Forte)
    with st.spinner('🌐 EXECUTANDO O BRAÇO FORTE (Selenium Headless)... Renderizando a página da SEFAZ para coleta cirúrgica...'):
        # Substitua a chamada abaixo pela sua função real de scraping
        dados_nota, lista_itens = raspar_dados_nfce(url_nfce)
        
    # 3. Verificação e Salvamento
    if dados_nota and lista_itens:
        
        # Resumo do Fiscalizador:
        total = dados_nota.get('valor_total', 0.0)
        
        st.markdown(f"""
        <div class="status-success">
            ✅ AUDITORIA CONCLUÍDA: **{len(lista_itens)} ITENS** IDENTIFICADOS.<br>
            💸 VALOR TOTAL DA TRANSAÇÃO: R$ **{total:.2f}**.<br>
            <br>
            **MISSÃO CUMPRIDA:** Dados prontos para análise!
        </div>
        """, unsafe_allow_html=True)
        
        with st.spinner('💾 SALVANDO PLANILHAS: Persistindo dados em formato CSV, como o Fiscalizador gosta...'):
            # Substitua a chamada abaixo pela sua função real de salvamento
            salvar_dados_em_csv(dados_nota, lista_itens, hash_qr) # Usa o hash_qr já calculado
        
        st.success(f"Planilhas **itens_nfce.csv** e **notas_nfce.csv** atualizadas em /{PASTA_DADOS}/")
        
    else:
        st.markdown(f"""
        <div class="status-error">
            ❌ FALHA NA AUDITORIA: Não foi possível extrair dados válidos.
            <br>
            **ORDEM:** Verifique a URL, a qualidade da imagem ou o log de erros do Selenium.
        </div>
        """, unsafe_allow_html=True)

# --- Interface Streamlit (Minimalista e Focada) ---

st.title("🔎 O Fiscalizador: Controle de Compras Fiscais")

st.markdown("""
<p style="text-align: center; color: #555;">
    Sua ferramenta zero desperdício. Meu único trabalho é transformar notas fiscais da SEFAZ em **dados estruturados CSV**.<br>
    **Nenhum gráfico. Apenas fatos.**
</p>
""", unsafe_allow_html=True)

st.markdown("---")

# --- Opção 1: Upload de Imagem QR Code ---
st.header("1. Câmera ou Imagem (QR Code)")

uploaded_file = st.file_uploader(
    "FORNEÇA A PROVA: Selecione a imagem (PNG/JPG) com o QR Code da NFC-e",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    st.image(uploaded_file, caption='Imagem de Origem', width=150)
    
    # Leitura do QR Code
    url_nfce_qr = extrair_url_qr_code(uploaded_file.read())
    
    if url_nfce_qr:
        st.info(f"URL DESTRAVADA: `{url_nfce_qr}`")
        if st.button("🚀 INICIAR AUDITORIA (Via QR Code)", key='btn_qr'):
            # Chamada para a função processar_nfce
            processar_nfce(url_nfce_qr)
    else:
        st.warning("⚠️ QR Code não detectado ou inválido. O Fiscalizador não aceita provas de baixa qualidade.")

st.markdown("---")

# --- Opção 2: Entrada Manual (URL ou Código) ---
st.header("2. Entrada Manual")

url_manual = st.text_input(
    "INSIRA A CHAVE: Cole aqui a URL completa ou o código de acesso da NFC-e:",
    key='url_manual_input',
    placeholder="Ex: http://nfe.sefaz.go.gov.br/nfeweb/sites/nfce/danfeNFCe?p=..."
)

if url_manual:
    url_processar = url_manual
    # Se não começar com http, ele presume que é uma chave, mas envia a chave para o processamento.
    # O SCRAPER DEVE SABER COMO MONTAR A URL COMPLETA COM BASE NO CÓDIGO!
        
    if st.button("🚀 INICIAR AUDITORIA (Via Código Manual)", key='btn_manual'):
        # Chamada para a função processar_nfce
        processar_nfce(url_processar)