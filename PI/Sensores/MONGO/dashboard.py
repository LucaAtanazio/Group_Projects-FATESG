import streamlit as st
import pandas as pd
import numpy as np
from pymongo import MongoClient
import joblib
import time

# -----------------------------
# CONFIGURAÇÕES DO DASHBOARD
# -----------------------------
st.set_page_config(
    page_title="Dashboard IoT + ML — Qualidade das Frutas",
    layout="wide"
)

st.title("Dashboard IoT + Machine Learning — Monitoramento das Frutas")


# -----------------------------
# CONEXÃO COM O MONGODB
# -----------------------------
MONGO_URI = "mongodb://localhost:27017"  # altere se precisar

try:
    client = MongoClient(MONGO_URI)
    db = client["banco_sensores"]
    colecao = db["leituras"]

    st.success("Conectado ao MongoDB!")
except:
    st.error("Erro ao conectar ao MongoDB")
    st.stop()


# -----------------------------
# CARREGAR MODELOS DE ML
# -----------------------------
modelo_estado = joblib.load("modelo_1_estado.pkl")
modelo_tempo = joblib.load("modelo_2_tempo_restante.pkl")
modelo_ident = joblib.load("modelo_4_identificacao_fruta.pkl")
modelo_alerta = joblib.load("modelo_extra_alerta.pkl")

mapa_frutas = {0: "Banana", 1: "Maçã", 2: "Tomate"}
mapa_estado = {0: "Normal", 1: "Atenção", 2: "Crítico"}

# -----------------------------
# FUNÇÃO PARA LER DADOS DO MONGO
# -----------------------------
def carregar_dados():
    dados = list(colecao.find().sort("_id", -1).limit(100))
    if len(dados) == 0:
        return pd.DataFrame()
    df = pd.DataFrame(dados)
    df = df.rename(columns={"mq3_raw": "mq03", "temperatura": "temperatura"})
    return df


# -----------------------------
# CARREGAR DADOS
# -----------------------------
df = carregar_dados()

if df.empty:
    st.warning("Nenhum dado disponível no banco ainda.")
    st.stop()

# Apenas colunas importantes:
df = df[["temperatura", "umidade_ar", "mq03_tensao", "mq3_raw", "fruta"]]

df = df.rename(columns={
    "umidade_ar": "umidade",
    "mq03_tensao": "tensao",
    "mq3_raw": "mq03"
})

# -----------------------------
# SELECIONAR ÚLTIMA AMOSTRA
# -----------------------------
ultima = df.iloc[0]

st.subheader("📥 Última leitura recebida")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Temperatura", f"{ultima['temperatura']:.1f} °C")
col2.metric("Umidade", f"{ultima['umidade']:.1f} %")
col3.metric("Gás MQ-03", f"{ultima['mq03']}")
col4.metric("Tensão MQ-03", f"{ultima['tensao']:.2f} V")

# -----------------------------
# APLICAR MODELOS
# -----------------------------
X_input = np.array([[ultima["temperatura"], ultima["umidade"], ultima["mq03"]]])

estado_pred = modelo_estado.predict(X_input)[0]
tempo_pred = modelo_tempo.predict(np.array([[ultima["temperatura"], ultima["umidade"], ultima["mq03"], ultima["fruta"]]]))[0]
fruta_pred = modelo_ident.predict(X_input)[0]
alerta_pred = modelo_alerta.predict(np.array([[ultima["temperatura"], ultima["umidade"], ultima["mq03"], fruta_pred, estado_pred]]))[0]

# -----------------------------
# EXIBIR PREVISÕES
# -----------------------------
st.subheader("🤖 Resultados da Inteligência Artificial")

colA, colB, colC, colD = st.columns(4)

colA.metric("Tipo de Fruta", mapa_frutas[fruta_pred])
colB.metric("Estado Atual", mapa_estado[estado_pred])
colC.metric("Tempo Estimado Restante", f"{tempo_pred:.1f} horas")
colD.metric("Alerta de Venda Rápida", "SIM 🚨" if alerta_pred == 1 else "Não")

# -----------------------------
# GRÁFICO DE TEMPO REAL
# -----------------------------
st.subheader("📈 Evolução do MQ-03 (Gás liberado pela fruta)")
st.line_chart(df["mq03"].head(50))

# -----------------------------
# TABELA COMPLETA
# -----------------------------
st.subheader("📋 Últimos registros do lote")
st.dataframe(df.head(50))

