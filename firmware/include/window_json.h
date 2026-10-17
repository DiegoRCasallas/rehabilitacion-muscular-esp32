#pragma once
#include <Arduino.h>
#include "config.h"
#include "sampler.h"

inline String windowToJson(const Window& w) {
  String body;
  body.reserve(WINDOW_SIZE * 6 + 64);
  body += "{\"sample_rate_hz\":" + String(SAMPLE_RATE_HZ) + ",\"samples\":[";
  for (size_t i = 0; i < WINDOW_SIZE; i++) {
    if (i) body += ',';
    body += w.mv[i];
  }
  body += "]}";
  return body;
}