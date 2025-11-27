#include "DHT.h"   // Biblioteca do sensor DHT

// --- CONFIGURAÇÕES DE HARDWARE DHT22 ---
#define DHTPIN 19        // GPIO onde o DATA do DHT22 está conectado
#define DHTTYPE DHT22    // Tipo do sensor

DHT dht(DHTPIN, DHTTYPE);

// --- CONFIGURAÇÕES DO MQ-3 ---
#define MQ3_PIN 32       // Entrada analógica do ESP32 (ADC)

// =======================================================
// SETUP
// =======================================================
void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("Iniciando sensores...");

  // Inicializa o DHT22
  dht.begin();
  delay(2000);  // Tempo de estabilização do DHT22
  
  Serial.println("Sensores iniciados com sucesso!");
}

// =======================================================
// LOOP
// =======================================================
void loop() {

  // -----------------------
  // LEITURA DO DHT22
  // -----------------------
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Falha na leitura do DHT22!");
  } else {
    Serial.println("===== DHT22 =====");
    Serial.print("Temperatura: ");
    Serial.print(temperature);
    Serial.println(" °C");

    Serial.print("Umidade: ");
    Serial.print(humidity);
    Serial.println(" %");
  }

  // -----------------------
  // LEITURA DO MQ-3
  // -----------------------
  int rawValue = analogRead(MQ3_PIN);
  float voltage = rawValue * (3.3 / 4095.0);

  Serial.println("===== MQ-3 =====");
  Serial.print("MQ-3 Raw: ");
  Serial.print(rawValue);
  Serial.print(" | Tensão: ");
  Serial.print(voltage);
  Serial.println(" V");

  Serial.println("==============================");
  Serial.println();

  delay(2000); // Intervalo entre leituras
}

