#pragma once
#include <Arduino.h>
#include "config.h"

struct Window {
  int16_t mv[WINDOW_SIZE];
};

class Sampler {
 public:
  Sampler(uint8_t pin, QueueHandle_t out) : pin_(pin), out_(out) {}

  void start() {
    analogSetPinAttenuation(pin_, ADC_11db);   // rango completo ~0 a 3.3 V
    xTaskCreatePinnedToCore(run, "sampler", 4096, this, 3, nullptr, 1);
  }

  void setActive(bool on) { active_ = on; }

 private:
  static void run(void* arg) {
    auto* self = static_cast<Sampler*>(arg);
    Window window;
    size_t n = 0;
    TickType_t last = xTaskGetTickCount();

    for (;;) {
      vTaskDelayUntil(&last, pdMS_TO_TICKS(1000 / SAMPLE_RATE_HZ));
      if (!self->active_) { n = 0; continue; }

      window.mv[n++] = analogReadMilliVolts(self->pin_);   // ya calibrado de fábrica
      if (n == WINDOW_SIZE) {
        if (xQueueSend(self->out_, &window, 0) != pdTRUE) {
          Serial.println("! cola llena: ventana descartada");
        }
        n = 0;
      }
    }
  }

  uint8_t pin_;
  QueueHandle_t out_;
  volatile bool active_ = false;
};