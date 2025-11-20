//Henrique Keigo Nakashima Minowa - RM:564091
//Eduardo Delorenzo Moraes - RM:561749
//Matheus Bispo Faria Barbosa - RM:562140

#include <WiFi.h>
#include <HTTPClient.h>
#include <DHTesp.h>

// ======== CONFIGURAÇÕES WI-FI ========
const char* WIFI_SSID     = "Wokwi-GUEST";
const char* WIFI_PASSWORD = "";

// ======== CONFIGURAÇÕES FIWARE / VM AZURE ========
// IMPORTANTE: precisa ter http://
const char* FIWARE_HOST    = "http://20.63.91.180";
const int   FIWARE_UL_PORT = 7896;   // Porta do IoT-Agent Ultralight
const char* API_KEY        = "comfortkey";
const char* DEVICE_ID      = "comfort001";

// Service headers (devem bater com os usados no Postman)
const char* FIWARE_SERVICE     = "skillhub";
const char* FIWARE_SERVICEPATH = "/";

// ======== PINAGEM (AJUSTE PARA O SEU DIAGRAMA) ========
// DHT22 no GPIO 15
const int DHT_PIN  = 15;
// LDR em um pino ANALÓGICO de verdade (GPIO 34, por exemplo)
const int LDR_PIN  = 34;

// Objeto do DHT
DHTesp dht;

void connectWiFi() {
  Serial.print("Conectando ao WiFi: ");
  Serial.println(WIFI_SSID);

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int retries = 0;
  while (WiFi.status() != WL_CONNECTED && retries < 30) {
    delay(500);
    Serial.print(".");
    retries++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi conectado!");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nFalha ao conectar no WiFi.");
  }
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  // Inicializa DHT
  dht.setup(DHT_PIN, DHTesp::DHT22);
  Serial.println("DHT22 inicializado.");

  // LDR como entrada analógica
  pinMode(LDR_PIN, INPUT);

  // Wi-Fi
  connectWiFi();
}

void loop() {
  // Se perdeu Wi-Fi, tenta reconectar
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi desconectado, reconectando...");
    connectWiFi();
  }

  // ======== LEITURAS DOS SENSORES ========
  TempAndHumidity data = dht.getTempAndHumidity();
  float temperature = data.temperature;  // °C
  float humidity    = data.humidity;     // %

  // Se leitura do DHT falhar, não envia nada nesse ciclo
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("ERRO: Leitura inválida do DHT (NaN). Não enviando neste ciclo.");
    delay(10000);
    return;
  }

  int rawLdr = analogRead(LDR_PIN);      // 0–4095 no ESP32
  // Converte para uma escala "0–100" de luminosidade
  float luminosity = map(rawLdr, 0, 4095, 0, 100);

  Serial.println("===== Medidas atuais =====");
  Serial.print("Temperatura: "); Serial.print(temperature); Serial.println(" °C");
  Serial.print("Umidade: ");     Serial.print(humidity);    Serial.println(" %");
  Serial.print("Luz (0-100): "); Serial.println(luminosity);
  Serial.println("==========================");

  // ======== MONTA PAYLOAD ULTRALIGHT ========
  // Formato: t|24.5|h|52.3|l|80
  String payload = "t|" + String(temperature, 1) +
                   "|h|" + String(humidity, 1) +
                   "|l|" + String(luminosity, 0);

  // ======== MONTA URL DO IOT-AGENT ========
  // Ex: http://SEU_IP_PUBLICO_AZURE:7896/iot/d?i=comfort001&k=comfortkey
  String url = String(FIWARE_HOST) + ":" + String(FIWARE_UL_PORT) +
               "/iot/d?i=" + DEVICE_ID +
               "&k=" + API_KEY;

  Serial.println("================================");
  Serial.print("Enviando para: ");
  Serial.println(url);
  Serial.print("Payload: ");
  Serial.println(payload);

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(url);

    http.addHeader("Content-Type", "text/plain");
    http.addHeader("Fiware-Service", FIWARE_SERVICE);
    http.addHeader("Fiware-ServicePath", FIWARE_SERVICEPATH);

    int httpCode = http.POST(payload);

    Serial.print("HTTP Code: ");
    Serial.println(httpCode);

    if (httpCode > 0) {
      String response = http.getString();
      Serial.print("Resposta: ");
      Serial.println(response);
    } else {
      Serial.print("Erro na requisição: ");
      Serial.println(http.errorToString(httpCode));
    }

    http.end();
  } else {
    Serial.println("Sem WiFi, não foi possível enviar.");
  }

  // Envia a cada 10 segundos (ajuste se quiser)
  delay(10000);
}
