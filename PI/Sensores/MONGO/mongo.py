from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# ================================
# 🔗 CONEXÃO COM O MONGODB
# ================================
client = MongoClient("mongodb://localhost:27017/")  # Altere se usar Mongo Atlas
db = client["IOTIA2"]                # Nome do banco
colecao = db["sensores"]             # Nome da coleção


# ================================
# ROTA PRINCIPAL
# ================================
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "mensagem": "API IoT ativa",
        "status": "OK"
    })


# ================================
# ROTA PARA RECEBER O JSON DO ESP32
# ================================
@app.route("/api/sensores", methods=["POST"])
def salvar_dados():
    try:
        dados = request.get_json()

        campos = ["temperatura", "umidade_ar", "mq3_raw", "mq3_tensao"]

        for c in campos:
            if c not in dados:
                return jsonify({"erro": f"Campo '{c}' ausente no JSON"}), 400

        dados["dataRegistro"] = datetime.now()

        resultado = colecao.insert_one(dados)

        return jsonify({
            "mensagem": "Dados recebidos e armazenados!",
            "id": str(resultado.inserted_id)
        }), 201

    except Exception as e:
        return jsonify({"erro": str(e)}), 500



# ================================
# INICIAR O SERVIDOR
# ================================
if __name__ == "__main__":
    app.run(host="172.31.3.10", port=8080, debug=True)
