/* reminder_manager.h */
#ifndef REMINDER_MANAGER_H
#define REMINDER_MANAGER_H

#include "config.h"
#include "time_manager.h"
#include "audio_player.h"
#include "server_communication.h"

extern Reminder reminders[MAX_REMINDERS];
extern SystemStatus systemStatus;

void executeReminder(int index) {
  if (index < 0 || index >= MAX_REMINDERS || !reminders[index].activo) return;
  
  Reminder& reminder = reminders[index];
  
  bool success = playReminderAudio(
    reminder.audioUrl,
    reminder.mensaje,
    reminder.medicamento
  );
}

void checkReminders() {
  String currentTime = getCurrentTime();
  if (currentTime.length() == 0) return;
  
  if (systemStatus.activeReminders == 0) return;
  
  for (int i = 0; i < MAX_REMINDERS; i++) {
    if (reminders[i].activo && reminders[i].hora == currentTime) {
      executeReminder(i);
    }
  }
}

void checkWaterReminder() {
  unsigned long currentTime = millis();
  int currentHour = getCurrentHour();
  
  if (currentHour >= WATER_START_HOUR && 
      currentHour <= WATER_END_HOUR &&
      currentTime - systemStatus.lastWaterReminder >= WATER_INTERVAL) {
    
    playWaterReminderAudio();
    sendWaterReminderEvent();
    systemStatus.lastWaterReminder = currentTime;
  }
}

#endif // REMINDER_MANAGER_H