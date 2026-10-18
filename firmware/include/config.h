#pragma once

#define WIFI_SSID       "DIEGO ♧ Galaxy A34"
#define WIFI_PASS       "nomeacuerdo"
#define SERVER_URL      "http://10.94.235.93:5000"
//10.94.235.163 -ip Asus conectado al celular Diego
//10.94.235.93 - Dirección IP HP conectado al celular Diego

//esto es para el websocket
#define SERVER_HOST     "10.94.235.93"
#define SERVER_PORT     5000

// Ids que ya existen en el servidor
#define PATIENT_ID      1
#define ACTIVITY_ID     1
#define CALIBRATION_ID  1

#define EMG_PIN         34     // ADC1
#define BUTTON_PIN      0      // botón BOOT de la placa
#define LED_PIN         2      // LED integrado

#define SAMPLE_RATE_HZ  1000
#define WINDOW_SIZE     200    // 200 ms por ventana
#define POT_TEST_MODE   0