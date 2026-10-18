#pragma once
#include <Arduino.h>
#include <esp_timer.h>
#include "config.h"

struct Window {
  int16_t mv[WINDOW_SIZE];
};

class Sampler {
 public:
  Sampler(uint8_t pin, QueueHandle_t out) : pin_(pin), out_(out) {}

  void start() {
    analogSetPinAttenuation(pin_, ADC_11db);   // rango completo ~0 a 3.3 V
    if (xTaskCreatePinnedToCore(run, "sampler", 4096, this, 3, &task_, 1) != pdPASS) {
      Serial.println("! no se pudo crear la tarea del muestreador");
      return;
    }

    esp_timer_create_args_t timerArgs = {};
    timerArgs.callback = notifyTask;
    timerArgs.arg = this;
    timerArgs.name = "emg_sample";
    if (esp_timer_create(&timerArgs, &timer_) != ESP_OK) {
      Serial.println("! no se pudo crear el temporizador del muestreador");
      vTaskDelete(task_);
      task_ = nullptr;
      return;
    }

    if (esp_timer_start_periodic(timer_, 1000000 / SAMPLE_RATE_HZ) != ESP_OK) {
      Serial.println("! no se pudo iniciar el temporizador del muestreador");
      esp_timer_delete(timer_);
      timer_ = nullptr;
      vTaskDelete(task_);
      task_ = nullptr;
    }
  }

  void setActive(bool on) { active_ = on; }

 private:
  static void notifyTask(void* arg) {
    auto* self = static_cast<Sampler*>(arg);
    if (self->task_ != nullptr) xTaskNotifyGive(self->task_);
  }

  static void run(void* arg) {
    auto* self = static_cast<Sampler*>(arg);
    Window window;
    size_t n = 0;

    for (;;) {
      ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
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
  TaskHandle_t task_ = nullptr;
  esp_timer_handle_t timer_ = nullptr;
  volatile bool active_ = false;
};