/* buzzer_controller.h  */
#ifndef BUZZER_CONTROLLER_H
#define BUZZER_CONTROLLER_H

#include "config.h"

#define NOTE_C4  262
#define NOTE_E4  330
#define NOTE_G4  392
#define NOTE_A4  440
#define NOTE_C5  523

void initBuzzer() {
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);
}

void playTone(int frequency, int duration) {
  if (frequency == 0) {
    delay(duration);
    return;
  }
  tone(BUZZER_PIN, frequency, duration);
  delay(duration);
  noTone(BUZZER_PIN);
}

void playBuzzerTone(ToneType type) {
  switch(type) {
    case TONE_WELCOME:
      playTone(NOTE_C4, 200);
      playTone(NOTE_E4, 200);
      playTone(NOTE_G4, 200);
      playTone(NOTE_C5, 400);
      break;
      
    case TONE_REMINDER:
      for (int i = 0; i < 3; i++) {
        playTone(NOTE_A4, 300);
        playTone(NOTE_C5, 300);
        delay(200);
      }
      break;
      
    case TONE_EMERGENCY:
      for (int i = 0; i < 6; i++) {
        playTone(NOTE_G4, 150);
        playTone(NOTE_C5, 150);
      }
      break;
      
    case TONE_SUCCESS:
      playTone(NOTE_C4, 150);
      playTone(NOTE_E4, 150);
      playTone(NOTE_G4, 150);
      playTone(NOTE_C5, 300);
      break;
      
    default:
      playTone(NOTE_C4, 500);
      break;
  }
}

void silenceBuzzer() {
  noTone(BUZZER_PIN);
  digitalWrite(BUZZER_PIN, LOW);
}

#endif // BUZZER_CONTROLLER_H