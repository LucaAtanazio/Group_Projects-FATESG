# Checklist de Aceitação - QR Fiscal Reader

## Critérios de Aceite Testáveis

### 1. Inicialização da Aplicação

- [ ] **CA-01**: Executar `streamlit run app.py` sem erros
  - **Passos:**
    1. Abrir terminal no diretório do projeto
    2. Executar: `streamlit run app.py`
    3. Verificar se abre navegador em `http://localhost:8501`
  - **Resultado Esperado:** Interface carrega sem erros

### 2. Leitura por Câmera

- [ ] **CA-02**: Webcam stream é exibido corretamente
  - **Passos:**
    1. Clicar na aba " Câmera"
    2. Clicar em " Iniciar Câmera"
    3. Verificar se o vídeo da webcam aparece
  - **Resultado Esperado:** Stream de vídeo em tempo real

- [ ] **CA-03**: QR Code é detectado e processado automaticamente
  - **Passos:**
    1. Iniciar câmera
    2. Posicionar QR Code de teste na frente da câmera
    3. Aguardar 1-2 segundos
  - **Resultado Esperado:** Mensagem " Cupom salvo com sucesso!"

### 3. Extração de Chave de Acesso

- [ ] **CA-04**: Extração de 44 dígitos puros
  - **Passos:**
    1. Usar fixture: `tests/fixtures/qr_pure_digits.png`
    2. Fazer upload na aba " Upload"
    3. Clicar em " Processar QR Code"
  - **Resultado Esperado:** Chave extraída: `12345678901234567890123456789012345678901234`

- [ ] **CA-05**: Extração de URL SEFAZ com parâmetro p=
  - **Passos:**
    1. Usar fixture: `tests/fixtures/qr_url_sefaz.png`
    2. Fazer upload e processar
  - **Resultado Esperado:** Chave extraída corretamente do parâmetro

- [ ] **CA-06**: Extração de URL com múltiplos parâmetros
  - **Passos:**
    1. Usar fixture: `tests/fixtures/qr_url_multiple_params.png`
    2. Fazer upload e processar
  - **Resultado Esperado:** Chave extraída ignorando outros parâmetros

### 4. Persistência em CSV

- [ ] **CA-07**: Dados salvos em fiscal_receipts.csv
  - **Passos:**
    1. Processar um QR Code válido
    2. Verificar se arquivo `fiscal_receipts.csv` foi criado
    3. Abrir arquivo e verificar colunas
  - **Resultado Esperado:** CSV com colunas: timestamp_iso, access_key, raw_data, source, device_id, image_saved

- [ ] **CA-08**: Todas as colunas são preenchidas corretamente
  - **Passos:**
    1. Processar QR Code
    2. Abrir CSV e verificar última linha
  - **Resultado Esperado:** 
    - timestamp_iso: formato ISO 8601
    - access_key: 44 dígitos
    - raw_data: dados do QR
    - source: "camera" ou "upload"
    - device_id: nome do computador
    - image_saved: "false"

### 5. Prevenção de Duplicatas

- [ ] **CA-09**: Duplicata em menos de 30s mostra aviso
  - **Passos:**
    1. Processar um QR Code
    2. Imediatamente processar o mesmo QR Code novamente
  - **Resultado Esperado:** Mensagem " Cupom já lido recentemente (últimos 30s)"

- [ ] **CA-10**: Duplicata não é salva no CSV
  - **Passos:**
    1. Processar QR Code
    2. Tentar processar novamente
    3. Verificar CSV
  - **Resultado Esperado:** Apenas 1 registro no CSV

- [ ] **CA-11**: Duplicata após 30s ainda é detectada
  - **Passos:**
    1. Processar QR Code
    2. Aguardar 35 segundos
    3. Processar mesmo QR Code
  - **Resultado Esperado:** Mensagem " Cupom já lido anteriormente"

### 6. Upload de Imagem

- [ ] **CA-12**: Upload de imagem funciona
  - **Passos:**
    1. Ir para aba " Upload"
    2. Clicar em "Browse files"
    3. Selecionar `tests/fixtures/qr_pure_digits.png`
  - **Resultado Esperado:** Imagem é exibida

- [ ] **CA-13**: Processamento de imagem extrai chave
  - **Passos:**
    1. Fazer upload de imagem com QR válido
    2. Clicar em "🔍 Processar QR Code"
  - **Resultado Esperado:** Chave extraída e salva

- [ ] **CA-14**: Imagem sem QR mostra erro apropriado
  - **Passos:**
    1. Fazer upload de imagem sem QR Code
    2. Clicar em processar
  - **Resultado Esperado:** Mensagem " Nenhum QR Code encontrado na imagem"

### 7. Visualização de Dados

- [ ] **CA-15**: Aba "Dados" mostra cupons registrados
  - **Passos:**
    1. Processar 3 QR Codes diferentes
    2. Ir para aba " Dados"
  - **Resultado Esperado:** Tabela com 3 registros

- [ ] **CA-16**: Estatísticas são calculadas corretamente
  - **Passos:**
    1. Processar 2 QR por câmera e 1 por upload
    2. Verificar métricas na aba "Dados"
  - **Resultado Esperado:**
    - Total: 3
    - Por Câmera: 2
    - Por Upload: 1

- [ ] **CA-17**: Download de CSV funciona
  - **Passos:**
    1. Clicar em " Baixar CSV"
    2. Verificar arquivo baixado
  - **Resultado Esperado:** Arquivo CSV válido com todos os dados

### 8. Validações e Erros

- [ ] **CA-18**: QR inválido (< 44 dígitos) é rejeitado
  - **Passos:**
    1. Usar fixture: `tests/fixtures/qr_invalid_short.png`
    2. Processar
  - **Resultado Esperado:** Mensagem " Nenhuma chave de acesso válida encontrada"

- [ ] **CA-19**: QR com caracteres não numéricos é rejeitado
  - **Passos:**
    1. Criar QR com "1234567890123456789012345678901234567890123A"
    2. Processar
  - **Resultado Esperado:** Rejeição

### 9. Testes Automatizados

- [ ] **CA-20**: Todos os testes unitários passam
  - **Passos:**
    1. Executar: `pytest tests/test_qr_utils.py -v`
  - **Resultado Esperado:** Todos os testes passam (0 failed)

- [ ] **CA-21**: Testes de storage passam
  - **Passos:**
    1. Executar: `pytest tests/test_storage.py -v`
  - **Resultado Esperado:** Todos os testes passam (0 failed)

- [ ] **CA-22**: Cobertura de testes > 90%
  - **Passos:**
    1. Executar: `pytest --cov=utils --cov-report=term`
  - **Resultado Esperado:** Coverage > 90%

### 10. Documentação

- [ ] **CA-23**: README.md está completo
  - **Passos:**
    1. Abrir README.md
    2. Verificar seções: Instalação, Uso, Testes, Estrutura
  - **Resultado Esperado:** Documentação clara e completa

- [ ] **CA-24**: docs/report.md está completo
  - **Passos:**
    1. Abrir docs/report.md
    2. Verificar seções técnicas e pedagógicas
  - **Resultado Esperado:** Relatório técnico detalhado

### 11. Fixtures de Teste

- [ ] **CA-25**: Imagens QR de teste foram geradas
  - **Passos:**
    1. Executar: `python scripts/generate_test_qr.py`
    2. Verificar diretório `tests/fixtures/`
  - **Resultado Esperado:** 6 imagens PNG criadas

---

## Resumo de Execução

**Data do Teste:** ___/___/______  
**Testador:** _______________________  
**Ambiente:** Windows / Linux / macOS  
**Python Version:** _______

**Resultados:**
- Total de Critérios: 25
- Aprovados: ___
- Reprovados: ___
- Não Testados: ___

**Status Final:** ✅ APROVADO / ❌ REPROVADO

**Observações:**
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
