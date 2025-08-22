/*
 * led_controller.h
 */

#ifndef LED_CONTROLLER_H
#define LED_CONTROLLER_H

#include "config.h"

extern Adafruit_NeoPixel rgbLed;

void initLEDs() {
  pinMode(LED_RED_PIN, OUTPUT);
  pinMode(LED_GREEN_PIN, OUTPUT);
  pinMode(LED_BLUE_PIN, OUTPUT);
  pinMode(LED_YELLOW_PIN, OUTPUT);
  
  digitalWrite(LED_RED_PIN, LOW);
  digitalWrite(LED_GREEN_PIN, LOW);
  digitalWrite(LED_BLUE_PIN, LOW);
  digitalWrite(LED_YELLOW_PIN, LOW);
  
  rgbLed.begin();
  rgbLed.setBrightness(70);
  rgbLed.show();
}

void setRGBColor(uint8_t red, uint8_t green, uint8_t blue) {
  rgbLed.setPixelColor(0, rgbLed.Color(red, green, blue));
  rgbLed.show();
}

void allLEDsOff() {
  digitalWrite(LED_RED_PIN, LOW);
  digitalWrite(LED_GREEN_PIN, LOW);
  digitalWrite(LED_BLUE_PIN, LOW);
  digitalWrite(LED_YELLOW_PIN, LOW);
  setRGBColor(0, 0, 0);
}

void allLEDsOn() {
  digitalWrite(LED_RED_PIN, HIGH);
  digitalWrite(LED_GREEN_PIN, HIGH);
  digitalWrite(LED_BLUE_PIN, HIGH);
  digitalWrite(LED_YELLOW_PIN, HIGH);
  setRGBColor(255, 255, 255); // Blanco brillante
  
  Serial.println("💡 Todos los LEDs encendidos (RED, GREEN, BLUE, YELLOW, RGB)");
}

void executePattern(PatternType type, bool isHot) {
  allLEDsOff();
  delay(100);
  
  uint8_t colors[6][3] = {{255,0,0}, {255,255,0}, {0,255,0}, {0,255,255}, {0,0,255}, {255,0,255}};
  uint8_t reminderColors[4][3] = {{255,0,0}, {255,255,0}, {0,255,0}, {0,0,255}};
  
  switch(type) {
    case PATTERN_EMERGENCY:
      Serial.println("🚨 Patrón: EMERGENCIA");
      for(int i = 0; i < 6; i++) {
        setRGBColor(255, 0, 0);
        digitalWrite(LED_RED_PIN, HIGH);
        delay(150);
        allLEDsOff();
        delay(150);
      }
      break;
      
    case PATTERN_SADNESS:
      Serial.println("😢 Patrón: TRISTEZA");
      for(int i = 0; i < 4; i++) {
        setRGBColor(0, 0, 255);
        digitalWrite(LED_BLUE_PIN, HIGH);
        delay(500);
        allLEDsOff();
        delay(500);
      }
      break;
      
    case PATTERN_HUNGER:
      Serial.println("🍽️ Patrón: HAMBRE");
      for(int i = 0; i < 4; i++) {
        setRGBColor(255, 255, 0);
        digitalWrite(LED_YELLOW_PIN, HIGH);
        delay(300);
        allLEDsOff();
        delay(300);
      }
      break;
      
    case PATTERN_TEMPERATURE:
      Serial.println("🌡️ Patrón: TEMPERATURA " + String(isHot ? "ALTA" : "BAJA"));
      if(isHot) {
        setRGBColor(255, 0, 0);
        for(int i = 0; i < 5; i++) {
          digitalWrite(LED_RED_PIN, HIGH);
          delay(200);
          digitalWrite(LED_RED_PIN, LOW);
          delay(200);
        }
      } else {
        setRGBColor(0, 100, 255);
        for(int i = 0; i < 5; i++) {
          digitalWrite(LED_BLUE_PIN, HIGH);
          delay(200);
          digitalWrite(LED_BLUE_PIN, LOW);
          delay(200);
        }
      }
      setRGBColor(0, 0, 0);
      break;
      
    case PATTERN_WATER:
      Serial.println("💧 Patrón: RECORDATORIO DE AGUA");
      for(int i = 0; i < 3; i++) {
        setRGBColor(0, 150, 255);
        digitalWrite(LED_BLUE_PIN, HIGH);
        digitalWrite(LED_GREEN_PIN, HIGH);
        delay(400);
        allLEDsOff();
        delay(400);
      }
      break;
      
    case PATTERN_SYSTEM_READY: {
      Serial.println("✅ Patrón: SISTEMA LISTO");
      for(int i = 0; i < 6; i++) {
        setRGBColor(colors[i][0], colors[i][1], colors[i][2]);
        delay(200);
      }
      setRGBColor(0, 0, 0);
      break;
    }
      
    case PATTERN_ERROR:
      Serial.println("❌ Patrón: ERROR");
      for(int i = 0; i < 10; i++) {
        setRGBColor(255, 0, 0);
        digitalWrite(LED_RED_PIN, HIGH);
        delay(100);
        allLEDsOff();
        delay(100);
      }
      break;
      
    case PATTERN_AUDIO_PLAYING:
      Serial.println("🎵 Patrón: REPRODUCIENDO AUDIO");
      for(int i = 0; i < 3; i++) {
        setRGBColor(255, 100, 255); // Rosa
        digitalWrite(LED_RED_PIN, HIGH);
        digitalWrite(LED_BLUE_PIN, HIGH);
        delay(500);
        
        setRGBColor(100, 255, 100); // Verde claro
        digitalWrite(LED_GREEN_PIN, HIGH);
        digitalWrite(LED_YELLOW_PIN, HIGH);
        delay(500);
        
        allLEDsOff();
        delay(200);
      }

      allLEDsOn();
      delay(2000);
      allLEDsOff();
      break;
      
    case PATTERN_REMINDER:
    default: 
      Serial.println("💊 Patrón: RECORDATORIO DE MEDICAMENTO");
      
      allLEDsOn();
      delay(1000);
      allLEDsOff();
      delay(500);
      
      for(int i = 0; i < 4; i++) {
        setRGBColor(reminderColors[i][0], reminderColors[i][1], reminderColors[i][2]);
        delay(300);
      }
      
      for(int i = 0; i < 3; i++) {
        digitalWrite(LED_RED_PIN, HIGH);
        digitalWrite(LED_GREEN_PIN, HIGH);
        digitalWrite(LED_BLUE_PIN, HIGH);
        digitalWrite(LED_YELLOW_PIN, HIGH);
        setRGBColor(255, 255, 255);
        delay(300);
        allLEDsOff();
        delay(300);
      }
      
      allLEDsOn();
      delay(3000);
      allLEDsOff();
      break;
  }
}

void emergencyLEDPattern() { executePattern(PATTERN_EMERGENCY, false); }
void sadnessLEDPattern() { executePattern(PATTERN_SADNESS, false); }
void hungerLEDPattern() { executePattern(PATTERN_HUNGER, false); }
void temperatureLEDPattern(bool isHot) { executePattern(PATTERN_TEMPERATURE, isHot); }
void waterReminderLEDPattern() { executePattern(PATTERN_WATER, false); }
void systemReadyLEDPattern() { executePattern(PATTERN_SYSTEM_READY, false); }
void errorLEDPattern(int errorCode) { executePattern(PATTERN_ERROR, false); }
void reminderLEDPattern() { executePattern(PATTERN_REMINDER, false); }

#endif // LED_CONTROLLER_H