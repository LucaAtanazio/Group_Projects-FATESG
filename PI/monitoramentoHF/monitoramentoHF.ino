#include <WiFi.h>              
#include <HTTPClient.h>        
#include "DHT.h"

// --- CONFIGURAÇÕES DE HARDWARE ---
#define DHTPIN 4           // Pino do DHT11
#define DHTTYPE DHT11      // Tipo do sensor
#define MQ3_ANALOG 25      // Entrada analógica do MQ-3 (A0)
#define MQ3_DIGITAL 18     // Entrada digital do MQ-3 (D0)

// --- CONFIGURAÇÕES DE REDE/SERVIÇO ---

const char* ssid = "NOME_DA_REDE"; 
const char* password = "SENHA_DA_REDE"; 
const char* serverURL = "http://[SEU_IP_DO_SERVIDOR]:3000/api/sensores"; 
String fruta = "banana"; // Lote de fruta sendo monitorado

// --- CONTROLE DE TEMPO ---
const long INTERVALO_ENVIO = 10000; // 10 segundos em milissegundos
unsigned long tempoAnterior = 0;   // Variável para armazenar o último tempo de envio

DHT dht(DHTPIN, DHTTYPE);

// =======================================================
// FUNÇÃO DE CONEXÃO WI-FI (NOVO)
// =======================================================
void conectarWiFi() {
  Serial.print("Conectando a ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  int tentativas = 0;
  while (WiFi.status() != WL_CONNECTED && tentativas < 20) {
    delay(500);
    Serial.print(".");
    tentativas++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("");
    Serial.println("Conexão Wi-Fi estabelecida!");
    Serial.print("Endereço IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("");
    Serial.println("Falha na conexão Wi-Fi. Reiniciando em 5s...");
    delay(5000);
    ESP.restart(); 
  }
}

// =======================================================
// FUNÇÃO DE ENVIO HTTP POST (NOVO)
// =======================================================
void enviarDados(float temp, float hum, int gasVal) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverURL);
    http.addHeader("Content-Type", "application/json");

    // Criação do objeto JSON (payload)
    String jsonPayload = "{";
    jsonPayload += "\"fruta\":\"" + fruta + "\",";
    jsonPayload += "\"temperatura\":" + String(temp, 1) + ","; 
    jsonPayload += "\"umidade\":" + String(hum, 1) + ",";      
    jsonPayload += "\"gasValue\":" + String(gasVal);           // Valor bruto do sensor MQ-3
    jsonPayload += "}";

    Serial.print("Enviando JSON: ");
    Serial.println(jsonPayload);

    // Envia o HTTP POST
    int httpResponseCode = http.POST(jsonPayload);

    if (httpResponseCode > 0) {
      Serial.print("Código de resposta HTTP: ");
      Serial.println(httpResponseCode);
    } else {
      Serial.print("Erro no envio HTTP: ");
      Serial.println(httpResponseCode);
      Serial.println(http.errorToString(httpResponseCode));
    }

    http.end(); // Fecha a conexão
  } else {
    Serial.println("Wi-Fi desconectado. Tentando reconectar...");
    conectarWiFi();
  }
}

// =======================================================
// SETUP (ALTERADO)
// =======================================================
void setup() {
  Serial.begin(115200);
  Serial.println("Iniciando sensores...");
  dht.begin();

  pinMode(MQ3_ANALOG, INPUT);
  pinMode(MQ3_DIGITAL, INPUT);

  // Conecta ao Wi-Fi antes de aquecer o sensor
  conectarWiFi();

  Serial.println("Aquecendo o sensor MQ-3...");
  delay(30000); // tempo de aquecimento (recomendado 20–30s)
  tempoAnterior = millis(); // Inicializa o contador de tempo após aquecimento
}

// =======================================================
// LOOP (ALTERADO)
// =======================================================
void loop() {
  // ----- Leitura dos Sensores (A cada 2 segundos) -----
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();
  int gasValue = analogRead(MQ3_ANALOG);

  // ----- Checagem de Erros e Impressão no Serial (mantido) -----
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Falha na leitura do sensor DHT11!");
  } else {
    Serial.println("=====================================");
    Serial.print("Temperatura: "); Serial.print(temperature); Serial.println(" °C");
    Serial.print("Umidade: "); Serial.print(humidity); Serial.println(" %");
    Serial.print("Nível de gás (analógico): "); Serial.println(gasValue);
  }

  // ----- Interpretação do nível (mantido) -----
  if (gasValue < 1000) {
    Serial.println("🍏 Baixo nível de etileno (fruta verde)");
  } else if (gasValue < 2000) {
    Serial.println("🍊 Nível moderado de etileno (fruta amadurecendo)");
  } else {
    Serial.println("🍎 Alto nível de etileno (fruta madura/passada)");
  }

  // =======================================================
  // CONTROLE DE TEMPO E ENVIO (NOVO/ALTERADO)
  // =======================================================
  unsigned long tempoAtual = millis();
  
  // Verifica se 10 segundos se passaram desde o último envio
  if (tempoAtual - tempoAnterior >= INTERVALO_ENVIO) {
    // Apenas envia se os dados do DHT11 forem válidos
    if (!isnan(humidity) && !isnan(temperature)) {
      enviarDados(temperature, humidity, gasValue);
    }
    // Atualiza o tempo anterior para o momento atual (reset do contador)
    tempoAnterior = tempoAtual;
  }
  
  // Mantém a leitura rápida a cada 2 segundos, mas o envio só ocorre a cada 10s
  delay(2000); 
}