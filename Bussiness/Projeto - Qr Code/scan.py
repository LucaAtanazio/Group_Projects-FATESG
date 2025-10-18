import streamlit as st
import pandas as pd
import re
import os
from datetime import datetime
from PIL import Image
import cv2
from pyzbar.pyzbar import decode
import numpy as np

# NOVAS IMPORTAÇÕES PARA STREAMING DE VÍDEO
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, VideoFrame

st.set_page_config(
    page_title="Leitor de QR Code Fiscal em Tempo Real",
    layout="wide"
)

# -------------------------------------------------------------------------
# VARIÁVEIS GLOBAIS E INICIALIZAÇÃO DO ESTADO DE SESSÃO
# -------------------------------------------------------------------------
CSV_FILE = "chaves_acesso.csv"

# Inicializa o estado da sessão para a chave lida, se não existir
if 'ultima_chave_lida' not in st.session_state:
    st.session_state['ultima_chave_lida'] = None
if 'status_ultima_chave' not in st.session_state:
    st.session_state['status_ultima_chave'] = None

# -------------------------------------------------------------------------
# FUNÇÕES DE LÓGICA DE DADOS
# -------------------------------------------------------------------------

def inicializar_csv():
    """Cria o arquivo CSV se ele não existir."""
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=['chave_acesso', 'data_leitura', 'status_duplicidade'])
        df.to_csv(CSV_FILE, index=False)

def extrair_chave_acesso(texto_qr):
    """Extrai a chave de acesso (44 dígitos) de uma string de QR Code fiscal."""
    padrao = r'p=(\d{44})' 
    match = re.search(padrao, texto_qr)
    if match:
        return match.group(1)
    return None

def verificar_duplicidade(chave):
    """Verifica se a chave de acesso já está presente no arquivo CSV."""
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        return chave in df['chave_acesso'].values
    return False

def salvar_chave(chave):
    """
    Salva a chave de acesso no CSV e atualiza o Session State de forma controlada.
    
    CORREÇÃO: A chave só é salva e o st.session_state atualizado se for uma 
    chave diferente da última lida, minimizando re-runs desnecessários.
    """
    
    # Se a chave detectada é a mesma que já está no estado, IGNORA o salvamento e re-run.
    if st.session_state.get('ultima_chave_lida') == chave:
        return 
    
    # 1. Processamento e Salvamento no CSV
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
    
    # 2. Atualiza o estado da sessão para que o Streamlit faça o re-run
    # e exiba o resultado na próxima execução.
    st.session_state['ultima_chave_lida'] = chave
    st.session_state['status_ultima_chave'] = status
    
    # O Streamlit deteta a alteração no st.session_state feita no thread secundário
    # e força o re-run no próximo ciclo, garantindo o feedback.

    return duplicada

# -------------------------------------------------------------------------
# CLASSE PROCESSADORA PARA O STREAMING EM TEMPO REAL
# -------------------------------------------------------------------------
class VideoProcessor(VideoProcessorBase):
    """
    Processa cada frame do stream de vídeo para detetar QR Codes.
    """
    def recv(self, frame: VideoFrame) -> VideoFrame:
        """
        Método de processamento principal: chamado para cada frame.
        """
        # Converte o frame para um array numpy do OpenCV (BGR)
        img = frame.to_ndarray(format="bgr")
        
        # O frame será modificado (desenhamos o retângulo verde)
        frame_processado = img.copy()
        
        # Deteta QR Codes usando pyzbar
        qr_codes = decode(frame_processado)
        
        for qr in qr_codes:
            dados = qr.data.decode('utf-8')
            
            # 1. Desenha o polígono verde (feedback visual)
            pontos = qr.polygon
            if pontos: # Verifica se a lista de pontos não está vazia
                pts = np.array(pontos, dtype=np.int32)
                # (0, 255, 0) é a cor verde em BGR
                cv2.polylines(frame_processado, [pts], True, (0, 255, 0), 5) 
            
            # 2. Extrai e salva a chave
            chave = extrair_chave_acesso(dados)
            
            if chave:
                # Chama a função de salvamento. O controle de duplicação está dentro da função.
                salvar_chave(chave) 
                
                # Para mostrar a chave diretamente no frame (feedback mais rápido)
                texto_feedback = f"CHAVE LIDA: {chave[:10]}..."
                cv2.putText(
                    frame_processado, 
                    texto_feedback,
                    (qr.rect.left, qr.rect.top - 10), # Posição acima do QR code
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    0.8, 
                    (0, 255, 0), # Cor verde
                    2,
                    cv2.LINE_AA
                )
                
        # Retorna o frame processado para ser exibido no Streamlit
        return VideoFrame.from_ndarray(frame_processado, format="bgr")

# -------------------------------------------------------------------------
# LÓGICA PRINCIPAL DO STREAMLIT
# -------------------------------------------------------------------------

# Inicializa o arquivo CSV se não existir
inicializar_csv()

st.title(" 📱 Leitor de QR Code Fiscal em Tempo Real")
st.markdown("### Escaneie cupons fiscais e extraia chaves de acesso automaticamente")

tab1, tab2, tab3 = st.tabs(["📷 Scanner em Tempo Real", "📊 Histórico", "ℹ️ Informações"])

with tab1:
    st.markdown("#### Aponte a câmera para o QR Code. A leitura é instantânea!")
    
    st.info("💡 Modo **Streaming de Vídeo**: O QR Code será contornado em verde e a chave será salva automaticamente ao ser reconhecida. A mensagem de feedback só aparece quando uma **nova** chave é identificada.")
    
    # Componente principal de streaming
    webrtc_streamer(
        key="leitor_qr_em_tempo_real",
        video_processor_factory=VideoProcessor, # Nossa classe processadora
        # Configuração STUN (necessária para WebRTC funcionar em muitas redes)
        rtc_configuration={ 
            "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}] 
        },
        media_stream_constraints={"video": True, "audio": False}, # Só precisamos de vídeo
        sendback_audio=False
    )
    
    st.markdown("---")

    # Feedback dinâmico da última leitura no Streamlit principal
    st.markdown("#### Resultado da Última Leitura Registrada")
    
    if st.session_state['ultima_chave_lida']:
        chave = st.session_state['ultima_chave_lida']
        status = st.session_state['status_ultima_chave']
        
        if status == 'Duplicada':
            st.warning(f"⚠️ **Chave Duplicada** (Registrada Automaticamente): `{chave}`")
        else:
            st.success(f"✅ **Nova Chave Identificada** (Salva Automaticamente): `{chave}`")
            
        st.markdown("---")
        
    else:
        st.info("Aguardando a detecção do primeiro QR Code...")
        
    # --- MODO ALTERNATIVO DE UPLOAD (MANTIDO) ---
    st.markdown("#### 🔄 Alternativa: Faça upload de uma imagem")
    arquivo_upload = st.file_uploader("Faça upload de uma imagem com QR code", type=['png', 'jpg', 'jpeg'])
    
    if arquivo_upload is not None:
        imagem = Image.open(arquivo_upload)
        imagem_array = np.array(imagem)
        
        # Conversão de cores para OpenCV (BGR)
        if len(imagem_array.shape) == 3 and imagem_array.shape[2] == 3:
            imagem_array = cv2.cvtColor(imagem_array, cv2.COLOR_RGB2BGR)
        
        # Lógica de processamento e feedback (mantida)
        qr_codes_upload = decode(imagem_array)
        frame_processado_upload = imagem_array.copy()
        chave_encontrada = None
        dados_completos = None
        
        for qr in qr_codes_upload:
            dados_completos = qr.data.decode('utf-8')
            pontos = qr.polygon
            if len(pontos) == 4:
                pts = np.array(pontos, dtype=np.int32)
                cv2.polylines(frame_processado_upload, [pts], True, (0, 255, 0), 3)
            chave_encontrada = extrair_chave_acesso(dados_completos)
            if chave_encontrada:
                break
        
        # Conversão de volta para Streamlit (RGB)
        if len(frame_processado_upload.shape) == 3:
            frame_processado_upload = cv2.cvtColor(frame_processado_upload, cv2.COLOR_BGR2RGB)
        
        st.image(frame_processado_upload, caption="Imagem processada", use_container_width=True)
        
        if chave_encontrada:
            st.success(f"✅ Chave de acesso detectada: `{chave_encontrada}`")
            
            if st.button("💾 Salvar chave de acesso (Upload)", key="btn_salvar_upload"):
                # Salvamento manual no upload
                duplicada = verificar_duplicidade(chave_encontrada)
                status_upload = "Duplicada" if duplicada else "Nova"
                
                nova_linha = pd.DataFrame({
                    'chave_acesso': [chave_encontrada],
                    'data_leitura': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                    'status_duplicidade': [status_upload]
                })
                
                df_csv = pd.read_csv(CSV_FILE)
                df_csv = pd.concat([df_csv, nova_linha], ignore_index=True)
                df_csv.to_csv(CSV_FILE, index=False)
                
                if duplicada:
                    st.warning("⚠️ Esta chave já foi registrada anteriormente!")
                else:
                    st.success("✅ Chave salva com sucesso!")
                st.rerun()

            with st.expander("Ver dados completos do QR code"):
                st.code(dados_completos)
        else:
            st.error("❌ Nenhuma chave de acesso encontrada na imagem")


# -------------------------------------------------------------------------
# CÓDIGO DO TAB2 E TAB3 (MANTIDO)
# -------------------------------------------------------------------------

with tab2:
    st.markdown("#### Histórico de chaves de acesso lidas")
    
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        
        if not df.empty:
           
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
            
         
            col1, col2 = st.columns(2)
            with col1:
                filtro_status = st.multiselect(
                    "Filtrar por status:",
                    options=['Nova', 'Duplicada'],
                    default=['Nova', 'Duplicada']
                )
            
           
            df_filtrado = df[df['status_duplicidade'].isin(filtro_status)]
            
           
            st.dataframe(
                df_filtrado.sort_values('data_leitura', ascending=False),
                use_container_width=True,
                hide_index=True
            )
            
            
            csv = df_filtrado.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=" Baixar dados (CSV)",
                data=csv,
                file_name=f"chaves_acesso_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            
          
            if st.button(" Limpar todo o histórico", type="secondary", key="btn_limpar_historico"):
                if st.checkbox("Confirmar exclusão de todos os dados", key="chk_confirmar_limpeza"):
                    os.remove(CSV_FILE)
                    inicializar_csv()
                    # Reseta o estado da sessão
                    st.session_state['ultima_chave_lida'] = None 
                    st.session_state['status_ultima_chave'] = None
                    st.success("Histórico limpo com sucesso!")
                    st.rerun()
        else:
            st.info(" Nenhuma chave de acesso registrada ainda.")
    else:
        st.info(" Nenhuma chave de acesso registrada ainda.")

with tab3:
    st.markdown("#### Como usar este aplicativo")
    
    st.markdown("""
    **Modo Scanner em Tempo Real (NOVO):**
    
    1.  Vá para a aba **"📷 Scanner em Tempo Real"**.
    2.  Conceda acesso à sua câmera.
    3.  **Aponte a câmera** para o QR Code do cupom fiscal.
    4.  Ao ser reconhecido, o QR Code será **contornado por um quadrado verde** no vídeo.
    5.  A chave de acesso é **salva automaticamente**.
    6.  A mensagem de feedback (Nova/Duplicada) só aparecerá na interface **quando uma chave diferente da anterior for detectada**, garantindo que a tela não fique a piscar.
    
    **Modo Alternativo (Upload):**
    
    1.  Faça o upload de uma imagem do seu QR Code.
    2.  Visualize o resultado e use o botão **"💾 Salvar chave de acesso (Upload)"** para registrar a chave.

    ---
    
    **Formato da chave de acesso:**
    - A chave de acesso é um número de 44 dígitos.
    """)
    
    st.markdown("---")
    st.markdown("**Bibliotecas utilizadas:**")
    st.code("""
    - streamlit
    - pandas
    - pyzbar
    - opencv-python (cv2)
    - numpy
    - streamlit-webrtc 
    """)