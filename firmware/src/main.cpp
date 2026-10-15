#include <Arduino.h>
#include <WiFi.h>
#include "api_client.h"
#include "config.h"
#include "sampler.h"

static QueueHandle_t windowQueue;
//static Sampler sampler(EMG_PIN, nullptr);   // se recrea abajo con la cola real
static ApiClient api(SERVER_URL);
static int sessionId = -1;

// Sampler necesita la cola, así que se construye en setup()
static Sampler* samplerPtr = nullptr;

static void connectWifi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.print("Conectando a WiFi");
  while (WiFi.status() != WL_CONNECTED) { delay(300); Serial.print('.'); }
  Serial.printf("\nIP: %s\n", WiFi.localIP().toString().c_str());
}

static bool buttonPressed() {
  static bool previous = HIGH;
  bool now = digitalRead(BUTTON_PIN);
  bool pressed = (previous == HIGH && now == LOW);
  previous = now;
  if (pressed) delay(40);   // antirrebote simple
  return pressed;
}

static void toggleSession() {
  if (sessionId < 0) {
    sessionId = api.startSession(PATIENT_ID, ACTIVITY_ID, CALIBRATION_ID);
    if (sessionId < 0) { Serial.println("No se pudo iniciar la sesión"); return; }
    xQueueReset(windowQueue);
    samplerPtr->setActive(true);
    Serial.printf("Sesión %d iniciada\n", sessionId);
  } else {
    samplerPtr->setActive(false);
    int finalScore = 0;
    if (api.closeSession(sessionId, finalScore)) {
      Serial.printf("Sesión %d cerrada. Puntaje final: %d\n", sessionId, finalScore);
    } else {
      Serial.println("No se pudo cerrar la sesión (el servidor la cerrará por inactividad)");
    }
    digitalWrite(LED_PIN, LOW);
    sessionId = -1;
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(LED_PIN, OUTPUT);

  connectWifi();

  windowQueue = xQueueCreate(5, sizeof(Window));
  samplerPtr = new Sampler(EMG_PIN, windowQueue);
  samplerPtr->start();

  Serial.println("Listo. Pulsa BOOT para iniciar o cerrar una sesión.");
}

void loop() {
  if (buttonPressed()) toggleSession();
  if (sessionId < 0) { delay(10); return; }

  Window window;
  if (xQueueReceive(windowQueue, &window, pdMS_TO_TICKS(50)) != pdTRUE) return;

  Feedback fb;
  if (api.sendWindow(sessionId, window, fb)) {
    digitalWrite(LED_PIN, fb.activation >= 0.5 ? HIGH : LOW);   // contracción efectiva
    Serial.printf("amp=%.0f mV  activación=%.2f  puntaje=%d\n",
                  fb.amplitude, fb.activation, fb.score);
  } else {
    Serial.println("! error enviando ventana");
  }
}