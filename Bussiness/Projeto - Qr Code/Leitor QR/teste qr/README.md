# 🧾 Leitor de Cupons Fiscais - QR Code Reader

Sistema de leitura de QR Codes de cupons fiscais em tempo real com extração automática de Chave de Acesso (44 dígitos).

**Desenvolvido para:** Faculdade SENAI FATESG - Disciplina Business Intelligence  
**Situação de Aprendizagem:** MERCADO EM NÚMEROS

---

## 📋 Descrição

Este sistema permite a leitura de QR Codes de cupons fiscais através de:
- **Câmera em tempo real** - Leitura automática via webcam
- **Upload de imagens** - Processamento de imagens salvas

O sistema extrai automaticamente a **Chave de Acesso** de 44 dígitos, evita duplicidades e armazena os dados em formato CSV para análise posterior.

---

## 🚀 Instalação

### Pré-requisitos

- Python 3.10 ou superior
- Webcam (opcional, para leitura em tempo real)
- Sistema operacional: Windows, Linux ou macOS

### Passo a Passo

1. **Clone ou baixe o projeto**

\`\`\`bash
git clone <repository-url>
cd qr-fiscal-reader
\`\`\`

2. **Crie um ambiente virtual (recomendado)**

\`\`\`bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
\`\`\`

3. **Instale as dependências**

\`\`\`bash
pip install -r requirements.txt
\`\`\`

4. **Execute a aplicação**

\`\`\`bash
streamlit run app.py
\`\`\`

A aplicação abrirá automaticamente no navegador em `http://localhost:8501`

---

## 📖 Como Usar

### Modo Câmera

1. Acesse a aba **"📷 Câmera"**
2. Clique em **"▶️ Iniciar Câmera"**
3. Posicione o QR Code do cupom fiscal na frente da câmera
4. O sistema detectará e processará automaticamente
5. Aguarde a mensagem de confirmação

**Dicas:**
- Mantenha boa iluminação
- Evite reflexos na tela do celular/papel
- Mantenha o QR Code estável por 1-2 segundos

### Modo Upload

1. Acesse a aba **"📤 Upload"**
2. Clique em **"Browse files"** e selecione uma imagem
3. Clique em **"🔍 Processar QR Code"**
4. Visualize o resultado do processamento

### Visualização de Dados

1. Acesse a aba **"📊 Dados"**
2. Visualize todos os cupons registrados
3. Veja estatísticas (total, por câmera, por upload)
4. Baixe os dados em CSV clicando em **"📥 Baixar CSV"**

---

## 🗂️ Estrutura do Projeto

\`\`\`
qr-fiscal-reader/
├── app.py                      # Aplicação Streamlit principal
├── utils/
│   ├── qr_utils.py            # Extração e validação de chaves
│   └── storage.py             # Persistência em CSV
├── tests/
│   ├── conftest.py            # Configuração pytest
│   ├── test_qr_utils.py       # Testes unitários
│   ├── test_storage.py        # Testes de persistência
│   └── fixtures/              # Imagens QR para testes
├── scripts/
│   └── generate_test_qr.py    # Gerador de QR codes de teste
├── docs/
│   └── report.md              # Relatório técnico detalhado
├── requirements.txt           # Dependências Python
├── architecture.json          # Arquitetura do sistema
├── fiscal_receipts.csv        # Dados salvos (gerado automaticamente)
└── README.md                  # Este arquivo
\`\`\`

---

## 🧪 Testes

### Executar Testes

\`\`\`bash
# Todos os testes
pytest

# Com cobertura
pytest --cov=utils --cov-report=html

# Testes específicos
pytest tests/test_qr_utils.py
pytest tests/test_storage.py
\`\`\`

### Gerar Imagens de Teste

\`\`\`bash
python scripts/generate_test_qr.py
\`\`\`

Isso criará imagens QR em `tests/fixtures/` para diferentes cenários de teste.

---

## 📊 Formato dos Dados

Os dados são salvos em `fiscal_receipts.csv` com as seguintes colunas:

| Coluna | Descrição | Exemplo |
|--------|-----------|---------|
| `timestamp_iso` | Data/hora da leitura | 2025-01-15T14:30:45.123456 |
| `access_key` | Chave de acesso (44 dígitos) | 12345678901234567890123456789012345678901234 |
| `raw_data` | Dados brutos do QR Code | https://www.sefaz.rs.gov.br/... |
| `source` | Origem (camera ou upload) | camera |
| `device_id` | Identificador do dispositivo | DESKTOP-ABC123 |
| `image_saved` | Imagem salva? | false |

---

## 🔧 Tecnologias Utilizadas

- **Streamlit** - Interface web interativa
- **OpenCV** - Processamento de imagem e captura de vídeo
- **pyzbar** - Decodificação de QR Codes
- **Pillow (PIL)** - Manipulação de imagens
- **Pandas** - Manipulação de dados
- **pytest** - Framework de testes

---

## ✅ Critérios de Aceite

- [x] `streamlit run app.py` exibe webcam stream
- [x] Extração correta da chave 44-dígitos de QR de exemplo
- [x] Salvamento em `fiscal_receipts.csv` com colunas definidas
- [x] Duplicata em <30s → "Cupom já lido" sem duplicação
- [x] Upload de imagem extrai corretamente
- [x] `pytest` roda sem erros para utilitários

---

## 🎓 Contexto Pedagógico

Este projeto faz parte da **Situação de Aprendizagem "MERCADO EM NÚMEROS"** da disciplina de Business Intelligence na Faculdade SENAI FATESG.

**Objetivos de Aprendizagem:**
- Coleta automatizada de dados de cupons fiscais
- Estruturação de dados para análise
- Desenvolvimento de aplicações práticas de BI
- Preparação de dados para dashboards analíticos

Os dados coletados serão utilizados posteriormente para:
- Análise de padrões de consumo
- Visualização de tendências de mercado
- Construção de dashboards interativos
- Estudos de caso em Business Intelligence

---

## 🐛 Solução de Problemas

### Câmera não funciona

- Verifique se a webcam está conectada e funcionando
- Tente fechar outros aplicativos que usam a câmera
- Use o modo Upload como alternativa

### Erro ao instalar pyzbar

**Windows:**
\`\`\`bash
# Baixe e instale o Visual C++ Redistributable
# Ou use: pip install pyzbar-windows
\`\`\`

**Linux:**
\`\`\`bash
sudo apt-get install libzbar0
\`\`\`

**macOS:**
\`\`\`bash
brew install zbar
\`\`\`

### QR Code não é detectado

- Melhore a iluminação
- Aproxime ou afaste o QR Code da câmera
- Certifique-se de que o QR Code está nítido (sem desfoque)
- Tente usar o modo Upload com uma foto de melhor qualidade

---

## 📝 Licença

Este projeto foi desenvolvido para fins educacionais na Faculdade SENAI FATESG.

---

## 👥 Autores

Desenvolvido para a disciplina de Business Intelligence - SENAI FATESG

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Consulte a documentação em `docs/report.md`
2. Verifique os testes em `tests/`
3. Entre em contato com o professor da disciplina
