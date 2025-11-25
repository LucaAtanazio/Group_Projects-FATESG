#include "DHT.h" 

// ==============================
// 1. CONFIGURAÇÃO DE PINO E TIPO
// ==============================
// O pino D4 na maioria das placas ESP32 corresponde ao GPIO 2
#define DHTPIN 4 
#define DHTTYPE DHT11

// Cria a instância do sensor DHT
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  Serial.println("--- Teste de Sensor DHT11 ---");
  dht.begin();
  delay(1000); // Pequena pausa para inicialização
}

void loop() {
  // O DHT11 só deve ser lido a cada 2 segundos (tempo mínimo de leitura)
  float umidade = dht.readHumidity();
  float temperatura = dht.readTemperature();

  // Verifica se a leitura foi bem-sucedida
  if (isnan(umidade) || isnan(temperatura)) {
    Serial.println("Falha na leitura do DHT11! Verifique a fiação no GPIO 2 (D4).");
    return;
  }

  // Exibe os resultados
  Serial.println("-------------------------");
  Serial.printf("🌡️ Temperatura: %.2f °C\n", temperatura);
  Serial.printf("💧 Umidade: %.2f %%\n", umidade);
  Serial.println("-------------------------");

  delay(2000); // Espera 2 segundos antes da próxima leitura
}