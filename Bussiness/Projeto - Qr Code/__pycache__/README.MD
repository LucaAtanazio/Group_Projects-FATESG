# 📱 Leitor de QR Code Fiscal

Aplicação web desenvolvida com Python e Streamlit para leitura e extração de chaves de acesso de cupons fiscais através de QR codes.

## 🚀 Funcionalidades

- ✅ Captura de QR codes através de câmera ao vivo ou upload de imagem
- ✅ Extração automática de chaves de acesso de 44 dígitos
- ✅ Validação e detecção de duplicatas
- ✅ Armazenamento em arquivo CSV
- ✅ Histórico completo de leituras
- ✅ Interface intuitiva em português
- ✅ Download de dados em CSV

## 📋 Requisitos

- Python 3.8 ou superior
- Bibliotecas listadas em `requirements.txt`

## 🔧 Instalação

1. Instale as dependências:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

2. Execute a aplicação:
\`\`\`bash
streamlit run scripts/app.py
\`\`\`

## 💡 Como usar

1. **Escolha o método de leitura**: Câmera ao vivo ou upload de imagem
2. **Posicione o QR code**: Certifique-se de que esteja visível e bem iluminado
3. **Capture ou faça upload**: Tire uma foto ou envie uma imagem
4. **Visualize o resultado**: A chave será extraída automaticamente
5. **Consulte o histórico**: Acesse a aba "Histórico" para ver todas as leituras

## 📊 Estrutura de dados

O arquivo CSV gerado contém:
- `chave_acesso`: Chave de 44 dígitos extraída
- `data_leitura`: Data e hora da leitura
- `status_duplicidade`: "Nova" ou "Duplicada"

## 🔍 Formato do QR Code

O aplicativo extrai chaves de QR codes no formato:
\`\`\`
http://nfe.sefaz.go.gov.br/nfeweb/sites/nfce/danfeNFCe?p=CHAVE_44_DIGITOS|...
\`\`\`

## 📝 Observações

- As chaves são salvas automaticamente no modo câmera
- No modo upload, é necessário clicar no botão "Salvar"
- O sistema detecta e marca chaves duplicadas
- Todos os dados são armazenados localmente em `chaves_acesso.csv`
