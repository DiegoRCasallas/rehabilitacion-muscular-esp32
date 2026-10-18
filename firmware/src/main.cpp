#include <Arduino.h>
#include <WiFi.h>
#include "api_client.h"
#include "config.h"
#include "sampler.h"
#include "stream_client.h"

enum class Mode { Idle, Game, Calibration };
enum class Press { None, Short, Long };

static QueueHandle_t windowQueue;
static Sampler* sampler = nullptr;
static ApiClient api(SERVER_URL);
static StreamClient stream;
static Mode mode = Mode::Idle;
static int targetId = -1;   // id de la sesión o de la calibración, según el modo

static void connectWifi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.print("Conectando a WiFi");
  while (WiFi.status() != WL_CONNECTED) { delay(300); Serial.print('.'); }
  Serial.printf("\nIP: %s\n", WiFi.localIP().toString().c_str());
}

// Distingue pulso corto y largo al soltar el botón
static Press readButton() {
  static bool down = false;
  static uint32_t since = 0;
  bool pressed = digitalRead(BUTTON_PIN) == LOW;
  if (pressed && !down) {
    down = true;
    since = millis();
  } else if (!pressed && down) {
    down = false;
    uint32_t held = millis() - since;
    if (held < 30) return Press::None;                 // rebote
    return held >= 1500 ? Press::Long : Press::Short;
  }
  return Press::None;
}

static void stopCurrent(const char* reason) {
  sampler->setActive(false);
  if (mode == Mode::Game) stream.end();
  digitalWrite(LED_PIN, LOW);
  Serial.printf("Detenido: %s\n", reason);
  mode = Mode::Idle;
  targetId = -1;
}

static void startGame() {
  int id = api.openSession(PATIENT_ID);
  if (id < 0) { Serial.println("No hay sesión abierta: pulsa «Iniciar» en el navegador"); return; }
  targetId = id;
  mode = Mode::Game;
  xQueueReset(windowQueue);
  stream.begin(id);
  sampler->setActive(true);
  Serial.printf("Unido a la sesión %d\n", id);
}

static void startCalibration() {
  int id = api.activeCalibrationRun(PATIENT_ID);
  if (id < 0) { Serial.println("No hay calibración en curso: pulsa «Iniciar calibración» en el navegador"); return; }
  targetId = id;
  mode = Mode::Calibration;
  xQueueReset(windowQueue);
  sampler->setActive(true);
  Serial.printf("Unido a la calibración %d\n", id);
}

static void showFeedback(const Feedback& fb) {
  digitalWrite(LED_PIN, fb.activation >= 0.5 ? HIGH : LOW);
  Serial.printf("amp=%.0f mV  activación=%.2f  puntaje=%d\n", fb.amplitude, fb.activation, fb.score);
}

static void handleGameWindow(const Window& window) {
  if (stream.connected()) {
    if (!stream.sendWindow(window)) Serial.println("! error enviando por WS");
  } else {
    Feedback fb;                                       // respaldo por HTTP
    if (api.sendWindow(targetId, window, fb)) showFeedback(fb);
  }
}

static void handleCalibrationWindow(const Window& window) {
  String phase;
  float amplitude = 0;
  int code = api.sendCalibrationWindow(targetId, window, phase, amplitude);
  if (code == 404) { stopCurrent("la calibración terminó en el navegador"); return; }
  if (code != 200) { Serial.println("! error enviando ventana de calibración"); return; }
  digitalWrite(LED_PIN, phase == "contraction" ? HIGH : LOW);   // LED = «contrae ahora»
  Serial.printf("[%s] amp=%.0f mV\n", phase.c_str(), amplitude);
}

void setup() {
  Serial.begin(115200);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(LED_PIN, OUTPUT);
  connectWifi();

  windowQueue = xQueueCreate(5, sizeof(Window));
  sampler = new Sampler(EMG_PIN, windowQueue);
  sampler->start();

  Serial.println("Listo. BOOT corto: unirse al juego. BOOT largo (2 s): unirse a la calibración.");
}

void loop() {
  Press press = readButton();
  if (press != Press::None) {
    if (mode != Mode::Idle) stopCurrent("botón");
    else if (press == Press::Long) startCalibration();
    else startGame();
  }
  if (mode == Mode::Idle) { delay(10); return; }

  if (mode == Mode::Game) stream.loop();

  Window window;
  if (xQueueReceive(windowQueue, &window, pdMS_TO_TICKS(10)) == pdTRUE) {
    if (mode == Mode::Game) handleGameWindow(window);
    else handleCalibrationWindow(window);
  }

  if (mode == Mode::Game) {
    Feedback fb;
    if (stream.takeFeedback(fb)) showFeedback(fb);
    if (stream.rejected()) stopCurrent("el servidor cerró la sesión");
  }
}