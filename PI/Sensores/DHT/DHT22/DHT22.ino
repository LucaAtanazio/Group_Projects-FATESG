#include "DHT.h"   // Biblioteca do sensor DHT

// --- CONFIGURAÇÕES DE HARDWARE DHT22 ---
#define DHTPIN 19        // GPIO onde o DATA do DHT22 está conectado
#define DHTTYPE DHT22    // Tipo do sensor agora é DHT22

// Cria a instância do sensor
DHT dht(DHTPIN, DHTTYPE);

// =======================================================
// SETUP
// =======================================================
void setup() {
  Serial.begin(115200);  
  Serial.println("Iniciando leitura do sensor DHT22...");

  dht.begin();  
  delay(2000);  // Tempo para estabilização do sensor
}

// =======================================================
// LOOP
// =======================================================
void loop() {

  float humidity = dht.readHumidity();        // Lê umidade
  float temperature = dht.readTemperature();  // Lê temperatura (Celsius)

  // Verifica falha de leitura
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Falha na leitura do DHT22! Verifique fios, alimentação e resistor.");
    return;  // Evita imprimir valores inválidos
  }

  Serial.println("=====================================");
  Serial.print("Temperatura: ");
  Serial.print(temperature);
  Serial.println(" °C");

  Serial.print("Umidade: ");
  Serial.print(humidity);
  Serial.println(" %");

  delay(2000); // O DHT22 aceita ~2s, mas é mais rápido que o DHT11
}
