import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, WebRtcMode
import cv2
from pyzbar import pyzbar
import pandas as pd
import numpy as np
import os
import re
from datetime import datetime, timedelta
from PIL import Image
import av
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(
    page_title="Scanner de QR Code Fiscal",
    page_icon="📷",
    layout="wide"
)

# Constantes
CSV_FILE = "fiscal_receipts.csv"
PROCESS_INTERVAL = 10  # Processar apenas a cada 10 frames para otimização

# Inicializar session state
if 'last_access_key' not in st.session_state:
    st.session_state.last_access_key = None
if 'last_status' not in st.session_state:
    st.session_state.last_status = None
if 'detected_key' not in st.session_state:
    st.session_state.detected_key = None
if 'detected_qr_data' not in st.session_state:
    st.session_state.detected_qr_data = None

# Funções de manipulação de dados
def extract_access_key(qr_data):
    """Extrai a chave de acesso de 44 dígitos da URL do QR Code"""
    if not qr_data:
        return None
    
    # Padrão para chave de acesso de 44 dígitos
    pattern = r'\b(\d{44})\b'
    match = re.search(pattern, qr_data)
    
    if match:
        return match.group(1)
    return None

def load_existing_keys():
    """Carrega as chaves de acesso já registradas do CSV"""
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE)
            return set(df['chave_acesso'].tolist())
        except:
            return set()
    return set()

def save_to_csv(access_key, qr_data, source):
    """Salva os dados no CSV e atualiza o session state"""
    existing_keys = load_existing_keys()
    
    # Verificar duplicidade
    if access_key in existing_keys:
        st.session_state.last_access_key = access_key
        st.session_state.last_status = "duplicate"
        return False
    
    # Preparar dados
    new_data = {
        'chave_acesso': access_key,
        'url_completa': qr_data,
        'data_leitura': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'fonte': source
    }
    
    # Salvar no CSV
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    else:
        df = pd.DataFrame([new_data])
    
    df.to_csv(CSV_FILE, index=False)
    
    st.session_state.last_access_key = access_key
    st.session_state.last_status = "success"
    return True

# Classe para processamento de vídeo com otimização
class QRVideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.frame_count = 0
        self.last_detected_data = None
        self.last_polygon = None
    
    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        self.frame_count += 1
        
        # Frame Skipping: processar apenas a cada PROCESS_INTERVAL frames
        if self.frame_count % PROCESS_INTERVAL == 0:
            # Converter para escala de cinza para detecção
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detectar QR Codes
            decoded_objects = pyzbar.decode(gray)
            
            if decoded_objects:
                for obj in decoded_objects:
                    qr_data = obj.data.decode('utf-8')
                    access_key = extract_access_key(qr_data)
                    
                    if access_key:
                        self.last_detected_data = {
                            'access_key': access_key,
                            'qr_data': qr_data
                        }
                        # Armazenar polígono para desenho
                        points = obj.polygon
                        if len(points) == 4:
                            self.last_polygon = np.array([
                                [point.x, point.y] for point in points
                            ], dtype=np.int32)
            else:
                # Limpar dados se nenhum QR Code for detectado
                if self.frame_count % (PROCESS_INTERVAL * 3) == 0:
                    self.last_detected_data = None
                    self.last_polygon = None
        
        # Desenhar feedback visual usando os últimos dados detectados
        if self.last_polygon is not None:
            cv2.polylines(img, [self.last_polygon], True, (0, 255, 0), 3)
        
        if self.last_detected_data:
            # Adicionar texto com a chave detectada
            text = f"Chave: {self.last_detected_data['access_key'][:20]}..."
            cv2.putText(img, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.7, (0, 255, 0), 2)
        
        return av.VideoFrame.from_ndarray(img, format="bgr24")

# Função para decodificar QR Code de imagem estática
def decode_qr_from_image(image):
    """Decodifica QR Code de uma imagem PIL"""
    # Converter PIL para numpy array
    img_array = np.array(image)
    
    # Converter para BGR se necessário
    if len(img_array.shape) == 3 and img_array.shape[2] == 3:
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    else:
        img_bgr = img_array
    
    # Converter para escala de cinza
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    
    # Decodificar QR Codes
    decoded_objects = pyzbar.decode(gray)
    
    results = []
    for obj in decoded_objects:
        qr_data = obj.data.decode('utf-8')
        access_key = extract_access_key(qr_data)
        if access_key:
            results.append({
                'access_key': access_key,
                'qr_data': qr_data
            })
    
    return results

# Handler para processar dados do vídeo no thread principal
def handle_inbound_track(ctx):
    """Callback para processar dados detectados no thread principal"""
    if hasattr(ctx.video_processor, 'last_detected_data'):
        data = ctx.video_processor.last_detected_data
        if data and data.get('access_key'):
            # Update detected key in session state without saving
            st.session_state.detected_key = data['access_key']
            st.session_state.detected_qr_data = data['qr_data']

# Função para gerar dados simulados de vendas para o dashboard de BI
def generate_mock_sales_data():
    """Gera dados simulados de vendas para o dashboard de BI"""
    np.random.seed(42)
    
    # Configurações
    num_records = 150
    produtos = ["Leite", "Pão", "Café", "Açúcar", "Carne", "Arroz", "Feijão", "Óleo"]
    formas_pagamento = ["Débito", "Crédito", "Dinheiro", "PIX"]
    
    # Gerar datas dos últimos 3 meses
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    dates = []
    for _ in range(num_records):
        random_days = np.random.randint(0, 90)
        random_hours = np.random.randint(8, 22)
        random_minutes = np.random.randint(0, 60)
        date = start_date + timedelta(days=random_days, hours=random_hours, minutes=random_minutes)
        dates.append(date)
    
    # Gerar dados
    data = {
        'data_hora': sorted(dates),
        'produto': np.random.choice(produtos, num_records),
        'quantidade': np.random.randint(1, 10, num_records),
        'preco_unitario': np.round(np.random.uniform(2.5, 50.0, num_records), 2),
    }
    
    df = pd.DataFrame(data)
    df['total_venda'] = np.round(df['quantidade'] * df['preco_unitario'], 2)
    df['forma_pagamento'] = np.random.choice(formas_pagamento, num_records)
    
    return df

# Interface do aplicativo
st.title("📷 Scanner de QR Code Fiscal")
st.markdown("Sistema de leitura automática de cupons fiscais em tempo real")

# Criar abas
tab1, tab2, tab3 = st.tabs(["📷 Scanner automático", "📤 Carregar imagem", "📊 Dashboard de Business Intelligence"])

# Aba 1: Scanner Automático
with tab1:
    st.header("Scanner em Tempo Real")
    st.markdown("Posicione o QR Code do cupom fiscal em frente à câmera")
    
    # Criar colunas para centralizar o vídeo
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # WebRTC streamer com callback
        ctx = webrtc_streamer(
            key="qr-scanner",
            mode=WebRtcMode.SENDRECV,
            video_processor_factory=QRVideoProcessor,
            media_stream_constraints={"video": True, "audio": False},
            async_processing=True,
        )
    
    # Display detected key if available
    st.divider()
    
    if st.session_state.detected_key:
        st.success(f"🎯 QR Code detectado!")
        st.code(st.session_state.detected_key, language=None)
    
    # Action buttons
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    
    with col_btn1:
        # Confirmation button - changes state based on detection
        if st.session_state.detected_key:
            if st.button("✅ Salvar Chave Detectada", type="primary", use_container_width=True):
                # Save to CSV when button is clicked
                if save_to_csv(
                    st.session_state.detected_key, 
                    st.session_state.detected_qr_data, 
                    'Scanner Automático'
                ):
                    st.success("✅ Cupom registrado com sucesso!")
                else:
                    st.warning("⚠️ Cupom já lido anteriormente!")
                
                # Clear detected key after saving
                st.session_state.detected_key = None
                st.session_state.detected_qr_data = None
                st.rerun()
        else:
            st.button("⏳ Aguardando QR Code...", disabled=True, use_container_width=True)
    
    with col_btn2:
        # Clear detection button
        if st.button("🔄 Limpar Detecção", use_container_width=True):
            st.session_state.detected_key = None
            st.session_state.detected_qr_data = None
            st.rerun()
    
    st.divider()
    
    # Mostrar feedback de leitura
    if st.session_state.last_access_key:
        if st.session_state.last_status == "success":
            st.success(f"✅ Cupom registrado com sucesso!")
            st.info(f"**Chave de Acesso:** `{st.session_state.last_access_key}`")
        elif st.session_state.last_status == "duplicate":
            st.warning(f"⚠️ Cupom já lido anteriormente!")
            st.info(f"**Chave de Acesso:** `{st.session_state.last_access_key}`")
    
    # Botão para limpar status
    if st.button("🔄 Limpar status"):
        st.session_state.last_access_key = None
        st.session_state.last_status = None
        st.rerun()

# Aba 2: Carregar Imagem
with tab2:
    st.header("Upload de Imagem")
    st.markdown("Faça upload de uma imagem contendo o QR Code do cupom fiscal")
    
    uploaded_file = st.file_uploader(
        "Escolha uma imagem",
        type=['png', 'jpg', 'jpeg'],
        help="Formatos aceitos: PNG, JPG, JPEG"
    )
    
    if uploaded_file is not None:
        # Mostrar imagem
        image = Image.open(uploaded_file)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(image, caption="Imagem carregada", use_container_width=True)
        
        # Processar imagem
        with st.spinner("Processando QR Code..."):
            results = decode_qr_from_image(image)
        
        if results:
            for result in results:
                access_key = result['access_key']
                qr_data = result['qr_data']
                
                st.success("✅ QR Code detectado!")
                st.info(f"**Chave de Acesso:** `{access_key}`")
                
                # Salvar no CSV
                if save_to_csv(access_key, qr_data, 'Upload Manual'):
                    st.success("✅ Cupom registrado com sucesso!")
                else:
                    st.warning("⚠️ Cupom já lido anteriormente!")
        else:
            st.error("❌ Nenhum QR Code válido encontrado na imagem")

# Aba 3: Ver Dados
with tab3:
    st.header("📊 Dashboard de Business Intelligence")
    st.markdown("Análise de vendas e indicadores de desempenho")
    
    # Gerar dados simulados
    df_sales = generate_mock_sales_data()
    
    # Converter coluna de data para datetime
    df_sales['data_hora'] = pd.to_datetime(df_sales['data_hora'])
    df_sales['data'] = df_sales['data_hora'].dt.date
    
    # Sidebar com filtros
    st.sidebar.header("🔍 Filtros")
    
    # Filtro de período
    min_date = df_sales['data'].min()
    max_date = df_sales['data'].max()
    
    date_range = st.sidebar.date_input(
        "Período",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        help="Selecione o intervalo de datas para análise"
    )
    
    # Filtro de produtos
    all_products = sorted(df_sales['produto'].unique().tolist())
    selected_products = st.sidebar.multiselect(
        "Produtos",
        options=all_products,
        default=all_products,
        help="Selecione um ou mais produtos"
    )
    
    # Filtro de forma de pagamento
    all_payments = sorted(df_sales['forma_pagamento'].unique().tolist())
    selected_payments = st.sidebar.multiselect(
        "Forma de Pagamento",
        options=all_payments,
        default=all_payments,
        help="Selecione as formas de pagamento"
    )
    
    # Aplicar filtros
    df_filtered = df_sales.copy()
    
    # Filtro de data
    if len(date_range) == 2:
        start_date, end_date = date_range
        df_filtered = df_filtered[
            (df_filtered['data'] >= start_date) & 
            (df_filtered['data'] <= end_date)
        ]
    
    # Filtro de produtos
    if selected_products:
        df_filtered = df_filtered[df_filtered['produto'].isin(selected_products)]
    
    # Filtro de forma de pagamento
    if selected_payments:
        df_filtered = df_filtered[df_filtered['forma_pagamento'].isin(selected_payments)]
    
    # Verificar se há dados após filtros
    if df_filtered.empty:
        st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados")
    else:
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_vendas = df_filtered['total_venda'].sum()
            st.metric("💰 Total de Vendas", f"R$ {total_vendas:,.2f}")
        
        with col2:
            num_vendas = len(df_filtered)
            st.metric("🛒 Número de Vendas", f"{num_vendas}")
        
        with col3:
            valor_medio = df_filtered['total_venda'].mean()
            st.metric("📊 Valor Médio por Venda", f"R$ {valor_medio:,.2f}")
        
        with col4:
            ticket_medio = df_filtered['preco_unitario'].mean()
            st.metric("🎫 Preço Médio Unitário", f"R$ {ticket_medio:,.2f}")
        
        st.divider()
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico 1: Total de Vendas por Dia
            st.subheader("📈 Total de Vendas por Dia")
            
            df_daily = df_filtered.groupby('data')['total_venda'].sum().reset_index()
            df_daily = df_daily.sort_values('data')
            
            fig1 = px.line(
                df_daily,
                x='data',
                y='total_venda',
                labels={'data': 'Data', 'total_venda': 'Total de Vendas (R$)'},
                markers=True
            )
            fig1.update_traces(line_color='#1f77b4', line_width=3)
            fig1.update_layout(
                hovermode='x unified',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Gráfico 2: Produtos Mais Vendidos
            st.subheader("🏆 Produtos Mais Vendidos")
            
            df_products = df_filtered.groupby('produto')['quantidade'].sum().reset_index()
            df_products = df_products.sort_values('quantidade', ascending=True)
            
            fig2 = px.bar(
                df_products,
                x='quantidade',
                y='produto',
                orientation='h',
                labels={'quantidade': 'Quantidade Vendida', 'produto': 'Produto'},
                color='quantidade',
                color_continuous_scale='Blues'
            )
            fig2.update_layout(
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # Segunda linha de gráficos
        col3, col4 = st.columns(2)
        
        with col3:
            # Gráfico 3: Comparativo de Formas de Pagamento
            st.subheader("💳 Vendas por Forma de Pagamento")
            
            df_payment = df_filtered.groupby('forma_pagamento')['total_venda'].sum().reset_index()
            
            fig3 = px.pie(
                df_payment,
                values='total_venda',
                names='forma_pagamento',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig3.update_traces(textposition='inside', textinfo='percent+label')
            fig3.update_layout(
                showlegend=True,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig3, use_container_width=True)
        
        with col4:
            # Gráfico 4: Vendas por Semana
            st.subheader("📅 Total de Vendas por Semana")
            
            df_filtered['semana'] = df_filtered['data_hora'].dt.to_period('W').astype(str)
            df_weekly = df_filtered.groupby('semana')['total_venda'].sum().reset_index()
            
            fig4 = px.bar(
                df_weekly,
                x='semana',
                y='total_venda',
                labels={'semana': 'Semana', 'total_venda': 'Total de Vendas (R$)'},
                color='total_venda',
                color_continuous_scale='Greens'
            )
            fig4.update_layout(
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig4, use_container_width=True)
        
        st.divider()
        
        # Tabela de dados detalhados
        st.subheader("📋 Dados Detalhados")
        
        # Preparar dados para exibição
        df_display = df_filtered[['data_hora', 'produto', 'quantidade', 'preco_unitario', 'total_venda', 'forma_pagamento']].copy()
        df_display['data_hora'] = df_display['data_hora'].dt.strftime('%d/%m/%Y %H:%M')
        df_display = df_display.sort_values('data_hora', ascending=False)
        
        # Renomear colunas para exibição
        df_display.columns = ['Data/Hora', 'Produto', 'Qtd', 'Preço Unit. (R$)', 'Total (R$)', 'Pagamento']
        
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        # Opções de exportação
        st.divider()
        st.subheader("📥 Exportar Dados")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            csv_data = df_display.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Baixar CSV",
                data=csv_data,
                file_name=f"vendas_dashboard_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        with col2:
            from io import BytesIO
            buffer = BytesIO()
            df_display.to_excel(buffer, index=False, engine='openpyxl')
            excel_data = buffer.getvalue()
            
            st.download_button(
                label="📥 Baixar Excel",
                data=excel_data,
                file_name=f"vendas_dashboard_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        with col3:
            # Resumo estatístico
            summary = f"""
            RESUMO DE VENDAS
            ================
            Período: {date_range[0] if len(date_range) > 0 else 'N/A'} a {date_range[1] if len(date_range) > 1 else 'N/A'}
            Total de Vendas: R$ {total_vendas:,.2f}
            Número de Vendas: {num_vendas}
            Valor Médio por Venda: R$ {valor_medio:,.2f}
            """
            
            st.download_button(
                label="📥 Baixar Resumo",
                data=summary,
                file_name=f"resumo_vendas_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
    
    # Informações sobre dados históricos de QR Codes
    st.divider()
    st.subheader("📷 Histórico de Cupons Fiscais")
    
    if os.path.exists(CSV_FILE):
        df_receipts = pd.read_csv(CSV_FILE)
        
        if not df_receipts.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total de Cupons", len(df_receipts))
            with col2:
                today = datetime.now().strftime('%Y-%m-%d')
                today_count = len(df_receipts[df_receipts['data_leitura'].str.contains(today)])
                st.metric("Leituras Hoje", today_count)
            with col3:
                scanner_count = len(df_receipts[df_receipts['fonte'] == 'Scanner Automático'])
                st.metric("Via Scanner", scanner_count)
            
            with st.expander("Ver detalhes dos cupons fiscais"):
                st.dataframe(
                    df_receipts[['chave_acesso', 'data_leitura', 'fonte']],
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.info("Nenhum cupom fiscal registrado ainda")
    else:
        st.info("Nenhum cupom fiscal registrado ainda")

# Rodapé
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p><strong>Sistema de Leitura de Cupons Fiscais</strong></p>
    <p>Projeto Acadêmico - Business Intelligence | FACULDADE SENAI FATESG</p>
</div>
""", unsafe_allow_html=True)
