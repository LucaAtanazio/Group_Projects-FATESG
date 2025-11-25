# Projeto integrador - Monitoramento Inteligente de Qualidade de Frutas (Hortifrúti IoT)

## Visão Geral do Projeto

- Este projeto de Arquitetura de Software e Sistemas Embarcados (IoT) visa solucionar o problema de **altas perdas e ineficiência operacional** na seção de Frutas, Legumes e Verduras (FLV) em varejos. O setor de FLV registrou uma **ineficiência operacional de 5,83% em 2024** , um índice que é mais do que o triplo da média geral do supermercado.

- Utilizamos uma arquitetura IoT baseada em sensores para coletar dados críticos de amadurecimento e conservação, aplicando um sistema de análise preditiva para gerar alertas de venda e descarte em tempo real.

### Frutas de Estudo (Casos Climatéricos):
* **Banana** 
* **Maçã** 
* **Tomate** 
> Frutos climatéricos aceleram a maturação e a degradação em cadeia devido à liberação do hormônio gasoso Etileno ($\text{C}_2\text{H}_4$)

## Arquitetura Funcional e Fluxo de Dados

O sistema segue uma arquitetura de **Edge Computing** e Nuvem, priorizando a **baixa latência e eficácia de rede** para que alertas de "Venda Rápida" cheguem à equipe em tempo hábil.

1.  **Módulo Edge (ESP32):** Realiza a coleta e o pré-processamento de dados brutos dos sensores. A inteligência na borda minimiza a latência ao formatar o payload JSON antes da transmissão
2.  **Comunicação:** Envia dados via Wi-Fi (MQTT/HTTP) para o servidor central.
3.  **Backend:** Normaliza, armazena e executa o Modelo de Decisão/IA.
4.  **Frontend/Consumidor:** Apresenta alertas e *dashboards* em tempo real para o usuário final.

### Componentes Chave

| Componente | Função no Projeto | Critério de Escolha / Detalhe Técnico |
| :--- | :--- | :--- |
| **Microcontrolador** | **ESP32 Dev Module** (Bluetooth/Wi-Fi) | Módulo Edge com capacidade de processamento e conectividade embarcada. |
| **Sensor de Gás** | **MQ-3 (Álcool/Etanol)**  | Utilizado como **proxy de baixo custo** para detectar Etanol e outros VOCs associados à deterioração e Etileno. |
| **Sensor Ambiental** | **DHT11** (Temperatura e Umidade) | Fornece dados essenciais, pois a temperatura e a umidade regulam o efeito catalítico do etileno. |
| **Linguagem Embarcada**| C++ (Arduino Framework) | Código: `monitoramentoHF.ino`. |
| **Comunicação** | HTTP POST | Endereço de Exemplo: `http://[SEU_IP_DO_SERVIDOR]:3000/api/sensores`. |
| **Intervalo de Envio** | **10 segundos** | **Observação:** O código `monitoramentoHF.ino` tem um *delay* de leitura de 2 segundos. A transmissão HTTP deve ser configurada para ocorrer a cada 10 segundos. |

## Configuração e Instalação

### 1. Requisitos de Hardware

* 1x Módulo ESP32 Dev Module
* 1x Sensor MQ-3
* 1x Sensor DHT11 (ou DHT22)
* 1x Resistor de Carga para o MQ-3 (Consultar datasheet, tipicamente 200 k$\Omega$)
* Fios e Protoboard

### 2. Configuração do Ambiente de Desenvolvimento (Arduino IDE)

Certifique-se de que o suporte à placa ESP32 esteja instalado no seu Arduino IDE.

#### A. Instalação de Bibliotecas
Este projeto requer as seguintes bibliotecas:

| Biblioteca | Instalação | Observação |
| :--- | :--- | :--- |
| **WiFi.h** | Incluída no suporte do ESP32 | Não requer instalação manual. |
| **HTTPClient.h** | Incluída no suporte do ESP32 | **Essencial** para requisições HTTP POST. |
| **DHT.h** |Gerenciador de Bibliotecas (por Adafruit) | **Requer a dependência "Adafruit Unified Sensor".** |

#### B. Setup do Código (`monitoramentoHF.ino`)

Antes de carregar o código no ESP32, as seguintes linhas devem ser atualizadas:

1.  **Credenciais Wi-Fi:**
    ```cpp
    const char* ssid = "NOME_DA_REDE"; 
    const char* password = "SENHA_DA_REDE"; 
    ```
2.  **Endpoint do Servidor:**
    ```cpp
    const char* serverURL = "http://[SEU_IP_DO_SERVIDOR]:3000/api/sensores"; 
    ```
3.  **Lote de Frutas (Teste):**
    ```cpp
    String fruta = "banana"; // Altere entre 'banana', 'maca' ou 'tomate'
    ```
4.  **Thresholds do Algoritmo de Regras (Leitura Bruta):**
    > Estes são os valores brutos (0-4095) utilizados pelo algoritmo de regras para classificar o status inicial da fruta no módulo Edge:
    ```cpp
    // Valores de referência do gasValue (MQ3_ANALOG)
    if (gasValue < 1000) { /* Verde */ } 
    else if (gasValue < 2000) { /* Amadurecendo */ } 
    else { /* Madura/Passada */ } 
    ```

### 3. Conexão dos Sensores (Pinagem)

| Sensor | Pino do Sensor | Pino do ESP32 (GPIO) | Tipo |
| :--- | :--- | :--- | :--- |
| **MQ-3 (Saída Analógica)** | A0 | **34** (`#define MQ3_PIN 34`) | Entrada Analógica |
| **DHT11 (Data)** | Vcc, GND, Data | **4** (`#define DHTPIN 4`) | Entrada/Saída Digital |
> *Observação:* O código utiliza `MQ3_ANALOG 25` e `DHTPIN 4` nas definições. Garanta que a sua placa ESP32 e a sua ligação física estejam mapeadas corretamente, sendo GPIO 34 e GPIO 4 os pinos físicos recomendados.

## Como Executar e Monitorar

1.  **Carregar:** Selecione a porta serial e o modelo do ESP32 no Arduino IDE e carregue o `monitoramentoHF.ino`.
2.  **Monitor Serial:** Abra o monitor serial (115200 baud) para verificar a conexão Wi-Fi e os dados crus coletados (Temperatura, Umidade, `gasValor`).
3.  **Backend:** Certifique-se de que o servidor Node.js (ou similar) esteja ativo no endereço IP configurado para receber o payload JSON via HTTP POST.
4.  **Análise:** O servidor processará o `gasValor` (dado bruto) em relação aos parâmetros de temperatura e umidade, gerando o alerta de amadurecimento/descarte.

## Contribuições

Este projeto foi desenvolvido pelos aludas do curso de *Inteligência Artificial* do 2° semestre na *SENAI FATESG* como trabalho de conclusão das disciplinas *(Internet das coisas / Projeto de Extensão Integrador)*.

* [@eopabro](https://github.com/eopabro) - Pablo Henrique: **Desenvolvimento e Implementação do Código Embarcado** (`monitoramentoHF.ino`), **Elaboração Conceitual do Projeto**, e **Pesquisa de Campo**.
* [@LucaAtanazio](https://github.com/LucaAtanazio) - Luca Atanazio: **Arquitetura e Apresentação do Projeto**, **Gerenciamento de Recursos e Aquisição de Hardware**, **Elaboração Conceitual do Projeto**, e **Pesquisa de Campo**.
---
### **Orientação Acadêmica**

O projeto foi concluído sob a direção dos professores:
* [Prof. Willgnner Ferreira Santos](https://github.com/Willgnner-Santos) *(Projeto de Extensão Integrador)*
* [Prof. Alisson Rodrigues](https://www.linkedin.com/in/alissonralves1/) *(Internet da Coisas)*

> **Licença:** MIT License [FACULDADE DE TEC SENAI DE DESENV.GERENCIAL / Uso Acadêmico]

