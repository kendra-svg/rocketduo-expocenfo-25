#ifndef TEMPERATURE_SENSOR_H
#define TEMPERATURE_SENSOR_H

#include "config.h"
#include "led_controller.h"
#include "server_communication.h"
#include <math.h>

inline void initTemperatureSensor() {
  #if defined(ESP32)
    analogSetWidth(12); // 0..4095
  #else
    analogReadResolution(12);
  #endif
}

inline float readTemperature() {
  float analogValue = analogRead(TEMP_SENSOR_PIN);

  #if defined(ESP32) && defined(ADC_11db)
    int mv = analogReadMilliVolts(TEMP_SENSOR_PIN);   
    float voltage = mv / 1000.0f;
  #else
    float voltage = (analogValue / 4095.0f) * 3.3f;
  #endif

  float temperature = (voltage - 0.5f) * 100.0f;

  if (temperature < -10.0f || temperature > 50.0f) {
    return 25.0f; 
  }
  return temperature;
}

inline void checkTemperature() {
  float temperature = readTemperature();
  systemStatus.lastTemperature = temperature;

  if (temperature < TEMP_MIN) {
    executePattern(PATTERN_TEMPERATURE, false);
    sendTemperatureAlert(temperature, "baja");
  } else if (temperature > TEMP_MAX) {
    executePattern(PATTERN_TEMPERATURE, true);
    sendTemperatureAlert(temperature, "alta");
  }
  sendTemperatureData(temperature);
}

#endif // TEMPERATURE_SENSOR_H
