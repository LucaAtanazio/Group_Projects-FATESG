#define MQ3_PIN 32  // Entrada analógica do ESP32

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("Iniciando leitura do sensor MQ-3...");
}

void loop() {
  int rawValue = analogRead(MQ3_PIN); // Lê o valor analógico (0–4095)
  
  // Converte opcionalmente para tensão (0–3.3V)
  float voltage = rawValue * (3.3 / 4095.0);

  Serial.print("MQ-3 Raw: ");
  Serial.print(rawValue);
  Serial.print(" | Tensão: ");
  Serial.print(voltage);
  Serial.println(" V");

  delay(500);
}
