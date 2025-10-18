# 📷 Scanner de QR Code Fiscal - Tempo Real

Sistema de captura e armazenamento de Chaves de Acesso de cupons fiscais eletrônicos (NFCe) com scanner em tempo real via webcam.

## 🎯 Funcionalidades

- ✅ **Scanner automático em tempo real** via webcam
- ✅ Leitura de QR Code via upload de imagem
- ✅ Extração automática da Chave de Acesso (44 dígitos)
- ✅ Controle de duplicidade
- ✅ Armazenamento em arquivo CSV
- ✅ Exportação em CSV, Excel e TXT
- ✅ Interface web intuitiva com três abas
- ✅ Otimização de performance com frame skipping
- ✅ Feedback visual em tempo real

## 🚀 Como Executar

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Webcam (para o scanner automático)

### Instalação

1. Clone ou baixe este projeto

2. Instale as dependências:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### Executar a Aplicação

\`\`\`bash
streamlit run scan.py
\`\`\`

A aplicação será aberta automaticamente no navegador em `http://localhost:8501`

## 📋 Como Usar

### Método 1: Scanner Automático (Recomendado)

1. Acesse a aba "📷 Scanner automático"
2. Permita o acesso à câmera quando solicitado
3. Posicione o QR Code do cupom fiscal em frente à câmera
4. O sistema irá:
   - Detectar automaticamente o QR Code
   - Desenhar um polígono verde ao redor do código
   - Extrair a Chave de Acesso
   - Verificar duplicidade
   - Salvar automaticamente no CSV

**Otimização de Performance:**
- O sistema processa apenas 1 a cada 10 frames para manter a fluidez do vídeo
- Feedback visual contínuo mesmo durante o processamento
- Detecção automática sem necessidade de cliques

### Método 2: Upload de Imagem

1. Acesse a aba "📤 Carregar imagem"
2. Clique em "Browse files" e selecione uma imagem contendo o QR Code
3. O sistema processará automaticamente e exibirá o resultado

### Visualizar Registros

1. Acesse a aba "📋 Ver dados"
2. Visualize todos os cupons lidos com métricas:
   - Total de cupons registrados
   - Leituras realizadas hoje
   - Quantidade via scanner automático
3. Exporte os dados em CSV, Excel ou TXT

## 🗄️ Estrutura de Dados

O sistema utiliza arquivo CSV (`fiscal_receipts.csv`) com a seguinte estrutura:

**Colunas:**
- `chave_acesso`: Chave de 44 dígitos (única)
- `url_completa`: URL completa do QR Code
- `data_leitura`: Data e hora da leitura
- `fonte`: Origem da leitura (Scanner Automático ou Upload Manual)

## 📦 Arquivos do Projeto

\`\`\`
.
├── scan.py                   # Aplicação principal
├── requirements.txt          # Dependências Python
├── README.md                # Documentação
└── fiscal_receipts.csv      # Dados (criado automaticamente)
\`\`\`

## 🛠️ Tecnologias

- **Streamlit**: Interface web
- **streamlit-webrtc**: Streaming de vídeo em tempo real
- **OpenCV**: Processamento de imagens e vídeo
- **pyzbar**: Decodificação de QR Codes
- **Pandas**: Manipulação de dados
- **Pillow**: Processamento de imagens
- **NumPy**: Operações numéricas
- **PyAV**: Processamento de frames de vídeo

## 🎥 Detalhes Técnicos do Scanner

### Otimização de Performance

O scanner utiliza a técnica de **Frame Skipping** para garantir fluidez:

- **PROCESS_INTERVAL = 10**: Processa apenas 1 a cada 10 frames
- **Todos os frames são exibidos**: Mantém vídeo fluido a ~30 FPS
- **Detecção assíncrona**: Não trava a interface durante o processamento

### Threading Seguro

- Processamento de vídeo em thread separada via `VideoProcessorBase`
- Salvamento de dados no thread principal via `in_bound_process_handler`
- Evita race conditions e garante integridade dos dados

### Feedback Visual

- Polígono verde desenhado ao redor do QR Code detectado
- Exibição da chave de acesso em tempo real
- Alertas de sucesso e duplicidade

## 📝 Exemplo de Uso

**URL do QR Code:**
\`\`\`
http://nfe.sefaz.go.gov.br/nfeweb/sites/nfce/danfeNFCe?p=52250339346861034147651070004999491107141815|2|1|1|DF46C0CAD32EF01BE6B47848D0D7BD145878E215
\`\`\`

**Chave de Acesso Extraída:**
\`\`\`
52250339346861034147651070004999491107141815
\`\`\`

## ⚠️ Controle de Duplicidade

O sistema impede o registro de cupons duplicados através de:
- Verificação da chave de acesso antes da inserção
- Comparação com registros existentes no CSV
- Mensagem de alerta: "⚠️ Cupom já lido anteriormente!"
- Atualização do session state para evitar salvamentos múltiplos

## 📊 Exportação de Dados

Os dados podem ser exportados em três formatos:
- **CSV**: Para análise em planilhas e importação em outros sistemas
- **Excel**: Para relatórios formatados com openpyxl
- **TXT**: Lista simples de chaves de acesso (uma por linha)

## 🔧 Solução de Problemas

### Câmera não funciona
- Verifique se o navegador tem permissão para acessar a câmera
- Teste em navegadores diferentes (Chrome recomendado)
- Verifique se outra aplicação não está usando a câmera

### QR Code não é detectado
- Certifique-se de que o QR Code está bem iluminado
- Mantenha o código a uma distância adequada da câmera
- Evite reflexos e borrões na imagem
- Use o modo de upload de imagem como alternativa

### Performance lenta
- O PROCESS_INTERVAL pode ser ajustado (valor maior = menos processamento)
- Feche outras aplicações que usam a câmera
- Verifique a resolução da câmera nas configurações

## 👨‍🎓 Projeto Acadêmico

**Curso**: Inteligência Artificial  
**Disciplina**: Business Intelligence  
**Instituição**: FACULDADE SENAI FATESG  
**Fase**: 1 - Scanner de QR Code para chaves de acesso em tempo real

## 📄 Licença

Projeto desenvolvido para fins educacionais.
