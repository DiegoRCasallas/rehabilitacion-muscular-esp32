#pragma once
#include <Arduino.h>
#include <ArduinoJson.h>
#include <WebSocketsClient.h>
#include "api_client.h"
#include "config.h"
#include "window_json.h"

class StreamClient {
 public:
  void begin(int sessionId) {
    String path = "/ws/sessions/" + String(sessionId) + "/device";
    ws_.begin(SERVER_HOST, SERVER_PORT, path);
    ws_.onEvent([this](WStype_t type, uint8_t* payload, size_t length) {
      onEvent(type, payload, length);
    });
    ws_.setReconnectInterval(2000);
    fresh_ = false;
  }

  void end() { ws_.disconnect(); connected_ = false; }
  void loop() { ws_.loop(); }
  bool connected() const { return connected_; }

  bool sendWindow(const Window& w) { return ws_.sendTXT(windowToJson(w)); }

  // true si llegó un feedback nuevo desde la última llamada
  bool takeFeedback(Feedback& out) {
    if (!fresh_) return false;
    out = latest_;
    fresh_ = false;
    return true;
  }

 private:
  void onEvent(WStype_t type, uint8_t* payload, size_t length) {
    switch (type) {
      case WStype_CONNECTED:    connected_ = true;  Serial.println("WS conectado"); break;
      case WStype_DISCONNECTED: connected_ = false; Serial.println("WS desconectado"); break;
      case WStype_TEXT: {
        JsonDocument doc;
        if (deserializeJson(doc, payload, length) || doc["activation"].isNull()) return;
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
  volatile bool connected_ = false;
  volatile bool fresh_ = false;
};