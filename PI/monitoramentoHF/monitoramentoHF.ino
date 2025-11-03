#include <WiFi.h>
#include <HTTPClient.h>
#include "DHT.h"

// --- CONFIGURAÇÕES DE REDE ---
const char* ssid = "NOME_DA_REDE";
const char* password = "SENHA_DA_REDE";
const char* serverURL = "http://192.168.1.10:3000/api/sensores"; // Endpoint da API

// --- SENSOR DHT11 ---
#define DHTPIN 4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// --- SENSOR MQ-3 ---
#define MQ3_PIN 34  // Entrada analógica

// --- VARIÁVEIS ---
String fruta = "banana";  // Altere para "maca" ou "tomate" conforme o lote

void setup() {
  Serial.begin(115200);
  dht.begin();

  Serial.println("Conectando ao Wi-Fi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWi-Fi conectado!");
}

void loop() {
  // --- Leitura dos sensores ---
  float temperatura = dht.readTemperature();
  float umidade = dht.readHumidity();
  int gasValor = analogRead(MQ3_PIN);

  if (isnan(temperatura) || isnan(umidade)) {
    Serial.println("Falha ao ler DHT11");
    return;
  }

  // --- Exibir no Serial ---
  Serial.println("==== Dados coletados ====");
  Serial.printf("Fruta: %s\n", fruta.c_str());
  Serial.printf("Temperatura: %.2f °C\n", temperatura);
  Serial.printf("Umidade: %.2f %%\n", umidade);
  Serial.printf("Nível de Gás (Etileno): %d\n", gasValor);
  Serial.println("=========================");

  // --- Enviar dados via HTTP POST ---
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverURL);
    http.addHeader("Content-Type", "application/json");

    String json = "{\"fruta\":\"" + fruta + "\","
                  "\"temperatura\":" + String(temperatura) + ","
                  "\"umidade\":" + String(umidade) + ","
                  "\"gas\":" + String(gasValor) + "}";

    int response = http.POST(json);

    if (response > 0)
      Serial.printf("Dados enviados! Código HTTP: %d\n", response);
    else
      Serial.printf("Falha no envio: %s\n", http.errorToString(response).c_str());

    http.end();
  } else {
    Serial.println("Wi-Fi desconectado!");
  }

  delay(10000); // Coleta a cada 10 segundos
}
