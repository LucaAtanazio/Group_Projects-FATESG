import streamlit as st
import pandas as pd
import re
import os
from datetime import datetime
from PIL import Image
import cv2
from pyzbar.pyzbar import decode
import numpy as np

# Configuração da página
st.set_page_config(
    page_title="Leitor de QR Code Fiscal",
    page_icon="📱",
    layout="wide"
)

# Nome do arquivo CSV
CSV_FILE = "chaves_acesso.csv"

# Função para inicializar o arquivo CSV
def inicializar_csv():
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=['chave_acesso', 'data_leitura', 'status_duplicidade'])
        df.to_csv(CSV_FILE, index=False)

# Função para extrair a chave de acesso do QR code
def extrair_chave_acesso(texto_qr):
    padrao = r'p=(\d{44})'
    match = re.search(padrao, texto_qr)
    if match:
        return match.group(1)
    return None

# Função para verificar duplicidade
def verificar_duplicidade(chave):
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        return chave in df['chave_acesso'].values
    return False

# Função para salvar chave no CSV
def salvar_chave(chave):
    duplicada = verificar_duplicidade(chave)
    status = "Duplicada" if duplicada else "Nova"
    
    nova_linha = pd.DataFrame({
        'chave_acesso': [chave],
        'data_leitura': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        'status_duplicidade': [status]
    })
    
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        df = pd.concat([df, nova_linha], ignore_index=True)
    else:
        df = nova_linha
    
    df.to_csv(CSV_FILE, index=False)
    return duplicada

# Função para processar frame da câmera
def processar_frame(frame):
    # Decodificar QR codes no frame
    qr_codes = decode(frame)
    
    for qr in qr_codes:
        # Extrair dados do QR code
        dados = qr.data.decode('utf-8')
        
        # Desenhar retângulo ao redor do QR code
        pontos = qr.polygon
        if len(pontos) == 4:
            pts = np.array(pontos, dtype=np.int32)
            cv2.polylines(frame, [pts], True, (0, 255, 0), 3)
        
        # Extrair chave de acesso
        chave = extrair_chave_acesso(dados)
        
        if chave:
            return frame, chave, dados
    
    return frame, None, None

# Inicializar CSV
inicializar_csv()

# Interface principal
st.title("📱 Leitor de QR Code Fiscal")
st.markdown("### Escaneie cupons fiscais e extraia chaves de acesso automaticamente")

# Criar abas
tab1, tab2, tab3 = st.tabs(["📷 Scanner", "📊 Histórico", "ℹ️ Informações"])

with tab1:
    st.markdown("#### Posicione o QR code do cupom fiscal na frente da câmera")
    
    # Opção de upload de imagem ou câmera
    opcao = st.radio("Escolha o método de leitura:", ["Câmera ao vivo", "Upload de imagem"])
    
    if opcao == "Upload de imagem":
        arquivo_upload = st.file_uploader("Faça upload de uma imagem com QR code", type=['png', 'jpg', 'jpeg'])
        
        if arquivo_upload is not None:
            # Ler imagem
            imagem = Image.open(arquivo_upload)
            imagem_array = np.array(imagem)
            
            # Converter para BGR se necessário
            if len(imagem_array.shape) == 3 and imagem_array.shape[2] == 3:
                imagem_array = cv2.cvtColor(imagem_array, cv2.COLOR_RGB2BGR)
            
            # Processar imagem
            frame_processado, chave, dados_completos = processar_frame(imagem_array)
            
            # Converter de volta para RGB para exibição
            if len(frame_processado.shape) == 3:
                frame_processado = cv2.cvtColor(frame_processado, cv2.COLOR_BGR2RGB)
            
            # Exibir imagem
            st.image(frame_processado, caption="Imagem processada", use_container_width=True)
            
            if chave:
                st.success(f"✅ Chave de acesso detectada: `{chave}`")
                
                # Salvar chave
                if st.button("💾 Salvar chave de acesso"):
                    duplicada = salvar_chave(chave)
                    if duplicada:
                        st.warning("⚠️ Esta chave já foi registrada anteriormente!")
                    else:
                        st.success("✅ Chave salva com sucesso!")
                    st.rerun()
                
                # Mostrar dados completos
                with st.expander("Ver dados completos do QR code"):
                    st.code(dados_completos)
            else:
                st.error("❌ Nenhuma chave de acesso encontrada na imagem")
    
    else:
        st.info("💡 **Modo câmera ao vivo**: Use o botão abaixo para capturar uma foto do QR code")
        
        # Captura de foto da câmera
        foto = st.camera_input("Tire uma foto do QR code")
        
        if foto is not None:
            # Processar foto
            imagem = Image.open(foto)
            imagem_array = np.array(imagem)
            
            # Converter para BGR
            if len(imagem_array.shape) == 3 and imagem_array.shape[2] == 3:
                imagem_array = cv2.cvtColor(imagem_array, cv2.COLOR_RGB2BGR)
            
            # Processar imagem
            frame_processado, chave, dados_completos = processar_frame(imagem_array)
            
            if chave:
                st.success(f"✅ Chave de acesso detectada: `{chave}`")
                
                # Salvar automaticamente
                duplicada = salvar_chave(chave)
                if duplicada:
                    st.warning("⚠️ Esta chave já foi registrada anteriormente!")
                else:
                    st.success("✅ Chave salva automaticamente!")
                
                # Mostrar dados completos
                with st.expander("Ver dados completos do QR code"):
                    st.code(dados_completos)
            else:
                st.error("❌ Nenhuma chave de acesso encontrada. Tente novamente com melhor iluminação.")

with tab2:
    st.markdown("#### Histórico de chaves de acesso lidas")
    
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        
        if not df.empty:
            # Estatísticas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total de leituras", len(df))
            with col2:
                novas = len(df[df['status_duplicidade'] == 'Nova'])
                st.metric("Chaves únicas", novas)
            with col3:
                duplicadas = len(df[df['status_duplicidade'] == 'Duplicada'])
                st.metric("Duplicadas", duplicadas)
            
            st.markdown("---")
            
            # Filtros
            col1, col2 = st.columns(2)
            with col1:
                filtro_status = st.multiselect(
                    "Filtrar por status:",
                    options=['Nova', 'Duplicada'],
                    default=['Nova', 'Duplicada']
                )
            
            # Aplicar filtros
            df_filtrado = df[df['status_duplicidade'].isin(filtro_status)]
            
            # Exibir tabela
            st.dataframe(
                df_filtrado.sort_values('data_leitura', ascending=False),
                use_container_width=True,
                hide_index=True
            )
            
            # Opção de download
            csv = df_filtrado.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Baixar dados (CSV)",
                data=csv,
                file_name=f"chaves_acesso_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            
            # Opção de limpar histórico
            if st.button("🗑️ Limpar todo o histórico", type="secondary"):
                if st.checkbox("Confirmar exclusão de todos os dados"):
                    os.remove(CSV_FILE)
                    inicializar_csv()
                    st.success("Histórico limpo com sucesso!")
                    st.rerun()
        else:
            st.info("📭 Nenhuma chave de acesso registrada ainda.")
    else:
        st.info("📭 Nenhuma chave de acesso registrada ainda.")

with tab3:
    st.markdown("#### Como usar este aplicativo")
    
    st.markdown("""
    **Passo a passo:**
    
    1. **Escolha o método de leitura**: Câmera ao vivo ou upload de imagem
    2. **Posicione o QR code**: Certifique-se de que o QR code esteja visível e bem iluminado
    3. **Capture ou faça upload**: Tire uma foto ou faça upload de uma imagem
    4. **Visualize o resultado**: A chave de acesso será extraída automaticamente
    5. **Salve a chave**: No modo upload, clique em "Salvar". No modo câmera, a chave é salva automaticamente
    
    **Formato da chave de acesso:**
    - A chave de acesso é um número de 44 dígitos
    - Exemplo: `52250339346861034147651070004999491107141815`
    
    **Detecção de duplicatas:**
    - O sistema verifica automaticamente se uma chave já foi registrada
    - Chaves duplicadas são marcadas no histórico
    
    **Armazenamento:**
    - Todas as chaves são salvas em um arquivo CSV
    - Você pode baixar o histórico completo a qualquer momento
    """)
    
    st.markdown("---")
    st.markdown("**Exemplo de QR code válido:**")
    st.code("http://nfe.sefaz.go.gov.br/nfeweb/sites/nfce/danfeNFCe?p=52250339346861034147651070004999491107141815|2|1|1|DF46C0CAD32EF01BE6B47848D0D7BD145878E215")
    
    st.markdown("**Bibliotecas utilizadas:**")
    st.code("""
    - streamlit
    - pandas
    - pyzbar
    - opencv-python (cv2)
    - PIL (Pillow)
    - numpy
    """)
