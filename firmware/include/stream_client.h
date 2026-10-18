#pragma once
#include <Arduino.h>
#include <ArduinoJson.h>
#include <WebSocketsClient.h>
#include "api_client.h"
#include "config.h"
#include "window_json.h"

class StreamClient {
 public:
  void beginSession(int sessionId) {
    open("/ws/sessions/" + String(sessionId) + "/device");
  }

  void beginCalibration(int runId) {
    open("/ws/calibration-runs/" + String(runId) + "/device");
  }

  void end() { ws_.disconnect(); connected_ = false; }
  void loop() { ws_.loop(); }
  bool connected() const { return connected_; }
  bool rejected() const { return rejected_; }

  bool sendWindow(const Window& w) {
    String payload = windowToJson(w);   // sendTXT pide String& no const
    return ws_.sendTXT(payload);
  }

  // true si llegó feedback de juego nuevo desde la última llamada
  bool takeFeedback(Feedback& out) {
    if (!fresh_) return false;
    out = latest_;
    fresh_ = false;
    return true;
  }

  // true si llegó estado de calibración nuevo desde la última llamada
  bool takeCalibration(String& phase, float& amplitude) {
    if (!calFresh_) return false;
    phase = calPhase_;
    amplitude = calAmplitude_;
    calFresh_ = false;
    return true;
  }

 private:
  void open(const String& path) {
    ws_.begin(SERVER_HOST, SERVER_PORT, path);
    ws_.onEvent([this](WStype_t type, uint8_t* payload, size_t length) {
      onEvent(type, payload, length);
    });
    ws_.setReconnectInterval(2000);
    fresh_ = false;
    calFresh_ = false;
    rejected_ = false;
  }

  void onEvent(WStype_t type, uint8_t* payload, size_t length) {
    switch (type) {
      case WStype_CONNECTED:    connected_ = true;  Serial.println("WS conectado"); break;
      case WStype_DISCONNECTED: connected_ = false; Serial.println("WS desconectado"); break;
      case WStype_TEXT: {
        JsonDocument doc;
        if (deserializeJson(doc, payload, length)) return;
        if (!doc["error"].isNull()) { rejected_ = true; return; }
        if (!doc["phase"].isNull()) {                       // respuesta de calibración
          calPhase_ = doc["phase"].as<String>();
          calAmplitude_ = doc["last_amplitude"].as<float>();
          calFresh_ = true;
          return;
        }
        if (doc["activation"].isNull()) return;             // respuesta de juego
        latest_.activation = doc["activation"].as<float>();
        latest_.amplitude  = doc["amplitude"].as<float>();
        latest_.score      = doc["score"].as<int>();
        fresh_ = true;
        break;
      }
      default: break;
    }
  }

  WebSocketsClient ws_;
  Feedback latest_;
  String calPhase_;
  float calAmplitude_ = 0;
  volatile bool connected_ = false;
  volatile bool fresh_ = false;
  volatile bool calFresh_ = false;
  volatile bool rejected_ = false;
};