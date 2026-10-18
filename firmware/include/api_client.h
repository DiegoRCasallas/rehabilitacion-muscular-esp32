#pragma once
#include <Arduino.h>
#include <ArduinoJson.h>
#include <HTTPClient.h>
#include "config.h"
#include "sampler.h"
#include "window_json.h"

struct Feedback
{
  float activation = 0;
  float amplitude = 0;
  int score = 0;
};

class ApiClient
{
public:
  explicit ApiClient(String baseUrl) : base_(std::move(baseUrl)) {}

  // Devuelve el id de la sesión o -1 si falla
  // int startSession(int patientId, int activityId, int calibrationId)
  // {
  //   String body = "{\"patient_id\":" + String(patientId) +
  //                 ",\"activity_id\":" + String(activityId) +
  //                 ",\"calibration_id\":" + String(calibrationId) + "}";
  //   JsonDocument doc;
  //   if (post("/sessions", body, doc) != 201)
  //     return -1;
  //   return doc["id"].as<int>();
  // }

  bool sendWindow(int sessionId, const Window &w, Feedback &out)
  {
    JsonDocument doc;
    if (post("/sessions/" + String(sessionId) + "/readings", windowToJson(w), doc) != 200)
      return false;
    out.activation = doc["activation"].as<float>();
    out.amplitude = doc["amplitude"].as<float>();
    out.score = doc["score"].as<int>();
    return true;
  }

  // bool closeSession(int sessionId, int &finalScore)
  // {
  //   JsonDocument doc;
  //   if (post("/sessions/" + String(sessionId) + "/close", "{}", doc) != 200)
  //     return false;
  //   finalScore = doc["score"].as<int>();
  //   return true;
  // }

  // Sesión abierta por el navegador, o -1
  int openSession(int patientId)
  {
    JsonDocument doc;
    if (get("/patients/" + String(patientId) + "/sessions/open", doc) != 200)
      return -1;
    return doc["id"].as<int>();
  }

  // Calibración iniciada en el navegador, o -1
  int activeCalibrationRun(int patientId)
  {
    JsonDocument doc;
    if (get("/patients/" + String(patientId) + "/calibration-runs/active", doc) != 200)
      return -1;
    return doc["run_id"].as<int>();
  }

  // Devuelve el código HTTP (200 = bien, 404 = la calibración ya terminó)
  int sendCalibrationWindow(int runId, const Window &w, String &phase, float &amplitude)
  {
    JsonDocument doc;
    int code = post("/calibration-runs/" + String(runId) + "/readings", windowToJson(w), doc);
    if (code == 200)
    {
      phase = doc["phase"].as<String>();
      amplitude = doc["last_amplitude"].as<float>();
    }
    return code;
  }

private:
  int post(const String &path, const String &body, JsonDocument &response)
  {
    HTTPClient http;
    http.begin(base_ + path);
    http.addHeader("Content-Type", "application/json");
    int code = http.POST(body);
    if (code > 0)
      deserializeJson(response, http.getString());
    http.end();
    return code;
  }
  int get(const String &path, JsonDocument &response)
  {
    HTTPClient http;
    http.begin(base_ + path);
    int code = http.GET();
    if (code > 0)
      deserializeJson(response, http.getString());
    http.end();
    return code;
  }

  String base_;
};