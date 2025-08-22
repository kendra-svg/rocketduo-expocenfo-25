/* button_handler.h */
#ifndef BUTTON_HANDLER_H
#define BUTTON_HANDLER_H

#include "config.h"
#include "led_controller.h"
#include "server_communication.h"

enum ButtonType {
  BUTTON_RED,    // Emergencia médica
  BUTTON_BLUE,   // Tristeza/soledad  
  BUTTON_YELLOW  // Hambre
};

static unsigned long lastButtonPress[3] = {0, 0, 0};
static const unsigned long debounceDelay = 200;

void initButtons() {
  pinMode(BUTTON_RED_PIN, INPUT_PULLUP);
  pinMode(BUTTON_BLUE_PIN, INPUT_PULLUP);
  pinMode(BUTTON_YELLOW_PIN, INPUT_PULLUP);
}

void handleButtonPress(ButtonType buttonType) {
  static const char* eventTypes[] = {"EMERGENCIA_MEDICA", "TRISTEZA_SOLEDAD", "HAMBRE"};
  static const PatternType patterns[] = {PATTERN_EMERGENCY, PATTERN_SADNESS, PATTERN_HUNGER};
  
  executePattern(patterns[buttonType]);
  sendEmergencyEvent(eventTypes[buttonType]);
}

void handleButtons() {
  unsigned long currentTime = millis();
  static const int buttonPins[] = {BUTTON_RED_PIN, BUTTON_BLUE_PIN, BUTTON_YELLOW_PIN};
  
  for (int i = 0; i < 3; i++) {
    if (digitalRead(buttonPins[i]) == LOW && 
        currentTime - lastButtonPress[i] > debounceDelay) {
      
      lastButtonPress[i] = currentTime;
      handleButtonPress((ButtonType)i);
    }
  }
}

#endif
 // BUTTON_HANDLER_H