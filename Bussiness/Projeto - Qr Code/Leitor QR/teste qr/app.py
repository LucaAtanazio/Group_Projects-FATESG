"""
Leitor QR Fiscal SEFAZ
Sistema de Leitura em Tempo Real de QR Codes Fiscais
Faculdade SENAI FATESG - Disciplina BI
"""

import streamlit as st
import cv2
import time
from datetime import datetime
from PIL import Image
import numpy as np
import av
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
from typing import Optional

from utils.qr_utils import (
    extract_access_key, 
    is_valid_access_key, 
    decode_qr_from_image,
    apply_auto_focus_simulation,
    calculate_sharpness
)
from utils.storage import save_receipt, is_duplicate, get_all_receipts

st.set_page_config(
    page_title="Leitor QR Fiscal SEFAZ",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stApp {
        background-color: #0e1117;
    }
    h1, h2, h3 {
        color: #00ff88 !important;
    }
    .status-reading {
        background-color: #1e3a5f;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #3b82f6;
        margin: 10px 0;
    }
    .status-success {
        background-color: #1e4d2b;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #00ff88;
        margin: 10px 0;
    }
    .status-error {
        background-color: #4d1e1e;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #ff4444;
        margin: 10px 0;
    }
    .recent-read {
        background-color: #1a1d24;
        padding: 10px;
        border-radius: 8px;
        margin: 8px 0;
        border-left: 3px solid #00ff88;
    }
</style>
""", unsafe_allow_html=True)

if 'last_reads' not in st.session_state:
    st.session_state.last_reads = []
if 'current_status' not in st.session_state:
    st.session_state.current_status = "Aguardando..."
if 'last_captured_frame' not in st.session_state:
    st.session_state.last_captured_frame = None
if 'capture_requested' not in st.session_state:
    st.session_state.capture_requested = False

RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

def process_qr_fiscal(qr_data: str, source: str = "camera") -> tuple[bool, str]:
    """
    Processa QR Code fiscal da SEFAZ e extrai chave de acesso
    
    Args:
        qr_data: Dados do QR Code
        source: Origem da leitura (camera/upload)
        
    Returns:
        Tupla (sucesso, mensagem)
    """
    access_key = extract_access_key(qr_data)
    
    if not access_key:
        return False, "Nenhum QR detectado"
    
    if not is_valid_access_key(access_key):
        return False, f"Chave inválida: {access_key}"
    
    if is_duplicate(access_key):
        return False, f"Cupom já lido anteriormente\nChave: {access_key[:20]}..."
    
    success = save_receipt(
        access_key=access_key,
        raw_data=qr_data,
        source=source
    )
    
    if success:
        st.session_state.last_reads.insert(0, {
            'key': access_key,
            'time': datetime.now().strftime('%H:%M:%S'),
            'source': source,
            'date': datetime.now().strftime('%d/%m/%Y')
        })
        st.session_state.last_reads = st.session_state.last_reads[:10]
        
        return True, f"Chave fiscal extraída com sucesso\n\n{access_key}"
    else:
        return False, "Erro ao salvar cupom"

class VideoProcessor:
    """Processador de vídeo para detecção em tempo real de QR codes"""
    
    def __init__(self):
        self.last_process_time = 0
        self.throttle_ms = 450  # Reduced from 200ms to 150ms for better responsiveness
        self.frame_with_box = None  # Added buffer for manual capture
        self.last_status = "Aguardando..."
    
    def recv(self, frame):
        """Processa cada frame do vídeo"""
        try:
            img = frame.to_ndarray(format="bgr24")
            
            current_time = time.time() * 1000
            
            # Throttle processing
            if current_time - self.last_process_time >= self.throttle_ms:
                self.last_process_time = current_time
                
                sharpness = calculate_sharpness(img)
                
                if sharpness < 100:
                    enhanced = apply_auto_focus_simulation(img, sharpness_threshold=100)
                else:
                    enhanced = img
                
                qr_data_list, qr_coords_list = decode_qr_from_image(enhanced)
                
                if qr_data_list:
                    st.session_state.current_status = "Lendo QR Code..."
                    
                    for coords in qr_coords_list:
                        x, y, w, h = coords
                        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 4)
                        
                        cv2.putText(
                            img, 
                            "QR DETECTADO", 
                            (x, y - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 
                            0.7, 
                            (0, 255, 0), 
                            2
                        )
                    
                
                    for qr_data in qr_data_list:
                        success, message = process_qr_fiscal(qr_data, source="camera")
                        
                        if success:
                            st.session_state.current_status = message
                            self.last_status = message
                            break
                        elif "já lido" in message:
                            st.session_state.current_status = message
                            self.last_status = message
                        else:
                            st.session_state.current_status = "Nenhum QR detectado"
                            self.last_status = "Nenhum QR detectado"
                else:
                    st.session_state.current_status = "Nenhum QR detectado"
                    self.last_status = "Nenhum QR detectado"
            
            self.frame_with_box = img.copy()
            
            return av.VideoFrame.from_ndarray(img, format="bgr24")
        
        except Exception as e:
            print(f"[v0] Erro no processamento de vídeo: {e}")
            return av.VideoFrame.from_ndarray(img, format="bgr24")

with st.sidebar:
    st.markdown("### 📋 Últimas 10 Leituras")
    
    if st.session_state.last_reads:
        for idx, read in enumerate(st.session_state.last_reads, 1):
            st.markdown(f"""
            <div class="recent-read">
                <strong>#{idx} - {read['time']}</strong><br>
                <small>{read['date']} | {read['source']}</small><br>
                <code style="font-size: 10px;">{read['key'][:20]}...</code>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Nenhuma leitura registrada")
    

st.markdown("#  Leitor QR Fiscal SEFAZ")
st.markdown("**Sistema de Leitura em Tempo Real de QR Codes Fiscais**")
st.markdown("---")

tab1, tab2, tab3 = st.tabs([" Câmera em Tempo Real", " Upload de Imagem", " Dashboard"])

with tab1:
    st.markdown("###  Leitura em Tempo Real")
    st.markdown("Posicione o QR Code fiscal da SEFAZ na frente da câmera para leitura automática")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        ctx = webrtc_streamer(
            key="qr-reader",
            mode=WebRtcMode.SENDRECV,
            rtc_configuration=RTC_CONFIGURATION,
            video_processor_factory=VideoProcessor,
            media_stream_constraints={"video": True, "audio": False},
            async_processing=True,
        )
        
        st.markdown("---")
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("📸 Capturar Foto", key="capture_btn"):
                if ctx.video_processor:

                    if hasattr(ctx.video_processor, 'frame_with_box') and ctx.video_processor.frame_with_box is not None:
                        frame = ctx.video_processor.frame_with_box
                        

                        qr_data_list, qr_coords_list = decode_qr_from_image(frame)
                        
                        if qr_data_list:
                            for qr_data in qr_data_list:
                                success, message = process_qr_fiscal(qr_data, source="camera_manual")
                                
                                if success:
                                    st.success(message)
                                elif "já lido" in message:
                                    st.warning(message)
                                else:
                                    st.info(message)
                        else:
                            st.error("Nenhum QR detectado na captura")
                    else:
                        st.warning("Aguarde a inicialização da câmera")
                else:
                    st.warning("Câmera não está ativa")
        
        with col_btn2:
            if st.button("🔄 Limpar Status", key="clear_btn"):
                st.session_state.current_status = "Aguardando..."
                st.rerun()
        
        st.markdown("### 📊 Status da Leitura")
        
        status = st.session_state.current_status
        
        if "sucesso" in status.lower():
            st.markdown(f"""
            <div class="status-success">
                <h4 style="color: #00ff88; margin: 0;"> Sucesso!</h4>
                <p style="margin: 5px 0 0 0;">{status}</p>
            </div>
            """, unsafe_allow_html=True)
        elif "lendo" in status.lower():
            st.markdown(f"""
            <div class="status-reading">
                <h4 style="color: #3b82f6; margin: 0;"> {status}</h4>
            </div>
            """, unsafe_allow_html=True)
        elif "nenhum" in status.lower():
            st.markdown(f"""
            <div class="status-error">
                <h4 style="color: #ff4444; margin: 0;"> {status}</h4>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info(status)
    
    with col2:
        st.markdown("###  Instruções")
        st.markdown("""
        **Como usar:**
        
        1.  Permita acesso à câmera
        2.  Posicione o QR Code
        3.  Aguarde o retângulo verde
        4.  Leitura automática
        
        **Dicas:**
        -  Boa iluminação
        -  QR Code centralizado
        -  Distância adequada
        -  Evite reflexos
        
        **Captura Manual:**
        -  Use o botão se a leitura automática falhar
        """)
        
with tab2:
    st.markdown("###  Upload de Imagem com QR Code")
    
    uploaded_file = st.file_uploader(
        "Selecione uma imagem contendo QR Code fiscal",
        type=["png", "jpg", "jpeg", "bmp"],
        help="Formatos aceitos: PNG, JPG, JPEG, BMP"
    )
    
    if uploaded_file is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            image = Image.open(uploaded_file)
            st.image(image, caption="Imagem Original", use_container_width=True)
        
        with col2:
            with st.spinner(" Processando imagem..."):
                img_array = np.array(image)
                
                if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                    img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                
                enhanced = apply_auto_focus_simulation(img_array)
                
                qr_data_list, qr_coords_list = decode_qr_from_image(enhanced)
                
                if not qr_data_list:
                    st.error(" Nenhum QR Code detectado na imagem")
                else:
                    img_with_boxes = img_array.copy()
                    for coords in qr_coords_list:
                        x, y, w, h = coords
                        cv2.rectangle(img_with_boxes, (x, y), (x + w, y + h), (0, 255, 0), 4)
                    
                    img_with_boxes_rgb = cv2.cvtColor(img_with_boxes, cv2.COLOR_BGR2RGB)
                    st.image(img_with_boxes_rgb, caption="QR Codes Detectados", use_container_width=True)
                    
                    st.markdown("---")
                    
                    for idx, qr_data in enumerate(qr_data_list, 1):
                        st.markdown(f"**QR Code #{idx}:**")
                        
                        success, message = process_qr_fiscal(qr_data, source="upload")
                        
                        if success:
                            st.success(message)
                        elif "já lido" in message:
                            st.warning(message)
                        else:
                            st.info(message)
                        
                        if idx < len(qr_data_list):
                            st.markdown("---")

with tab3:
    st.markdown("### Dashboard de Cupons Fiscais")
    
    df = get_all_receipts()
    
    if df.empty:
        st.info(" Nenhum cupom fiscal registrado ainda")
    else:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(" Total de Cupons", len(df))
        
        with col2:
            if 'source' in df.columns:
                camera_count = len(df[df['source'].str.contains('camera', na=False)])
                st.metric(" Lidos por Câmera", camera_count)
            else:
                st.metric(" Lidos por Câmera", "N/A")
        
        with col3:
            if 'source' in df.columns:
                upload_count = len(df[df['source'] == 'upload'])
                st.metric(" Lidos por Upload", upload_count)
            else:
                st.metric(" Lidos por Upload", "N/A")
        
        with col4:
            if 'timestamp' in df.columns and not df.empty:
                last_read = df.iloc[-1]['timestamp']
                time_part = last_read.split()[1] if ' ' in last_read else last_read
                st.metric(" Última Leitura", time_part)
            else:
                st.metric(" Última Leitura", "N/A")
        
        st.markdown("---")
        
        st.markdown("###  Chaves de Acesso Registradas")
        
        available_cols = []
        if 'timestamp' in df.columns:
            available_cols.append('timestamp')
        if 'access_key' in df.columns:
            available_cols.append('access_key')
        if 'source' in df.columns:
            available_cols.append('source')
        
        if available_cols:
            display_df = df[available_cols].copy()
            
            col_names = {}
            if 'timestamp' in display_df.columns:
                col_names['timestamp'] = 'Data/Hora'
            if 'access_key' in display_df.columns:
                col_names['access_key'] = 'Chave de Acesso'
            if 'source' in display_df.columns:
                col_names['source'] = 'Origem'
            
            display_df = display_df.rename(columns=col_names)
            
            st.dataframe(
                display_df,
                hide_index=True,
                use_container_width=True
            )
        else:
            st.warning("Estrutura de dados inválida no CSV")
        
        st.markdown("---")
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=" Baixar CSV Completo",
            data=csv,
            file_name=f"cupons_fiscais_sefaz_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
