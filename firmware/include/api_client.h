#pragma once
#include <Arduino.h>
#include <ArduinoJson.h>
#include <HTTPClient.h>
#include "config.h"
#include "sampler.h"

struct Feedback {
  float activation = 0;
  float amplitude = 0;
  int score = 0;
};

class ApiClient {
 public:
  explicit ApiClient(String baseUrl) : base_(std::move(baseUrl)) {}

  // Devuelve el id de la sesión o -1 si falla
  int startSession(int patientId, int activityId, int calibrationId) {
    String body = "{\"patient_id\":" + String(patientId) +
                  ",\"activity_id\":" + String(activityId) +
                  ",\"calibration_id\":" + String(calibrationId) + "}";
    JsonDocument doc;
    if (post("/sessions", body, doc) != 201) return -1;
    return doc["id"].as<int>();
  }

  bool sendWindow(int sessionId, const Window& w, Feedback& out) {
    String body;
    body.reserve(WINDOW_SIZE * 6 + 64);
    body += "{\"sample_rate_hz\":" + String(SAMPLE_RATE_HZ) + ",\"samples\":[";
    for (size_t i = 0; i < WINDOW_SIZE; i++) {
      if (i) body += ',';
      body += w.mv[i];
    }
    body += "]}";

    JsonDocument doc;
    if (post("/sessions/" + String(sessionId) + "/readings", body, doc) != 200) return false;
    out.activation = doc["activation"].as<float>();
    out.amplitude  = doc["amplitude"].as<float>();
    out.score      = doc["score"].as<int>();
    return true;
  }

  bool closeSession(int sessionId, int& finalScore) {
    JsonDocument doc;
    if (post("/sessions/" + String(sessionId) + "/close", "{}", doc) != 200) return false;
    finalScore = doc["score"].as<int>();
    return true;
  }

 private:
  int post(const String& path, const String& body, JsonDocument& response) {
    HTTPClient http;
    http.begin(base_ + path);
    http.addHeader("Content-Type", "application/json");
    int code = http.POST(body);
    if (code > 0) deserializeJson(response, http.getString());
    http.end();
    return code;
  }

  String base_;
};