/* time_manager.h */
#ifndef TIME_MANAGER_H
#define TIME_MANAGER_H

#include "config.h"

void initTimeManager() {
  configTime(GMT_OFFSET_SEC, DAYLIGHT_OFFSET, NTP_SERVER1);
  
  int attempts = 0;
  struct tm timeinfo;
  
  while (!getLocalTime(&timeinfo) && attempts < 10) {
    delay(2000);
    attempts++;
  }
  
  if (attempts < 10) {
    Serial.println(F("Tiempo sincronizado"));
  }
}

String getCurrentTime() {
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    return "N/A";
  }
  
  char buffer[10];
  strftime(buffer, sizeof(buffer), "%H:%M", &timeinfo);
  return String(buffer);
}

String getFormattedTime() {
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    return "N/A";
  }
  
  char buffer[20];
  strftime(buffer, sizeof(buffer), "%H:%M:%S", &timeinfo);
  return String(buffer);
}

String getFormattedDateTime() {
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    return "N/A";
  }
  
  char buffer[30];
  strftime(buffer, sizeof(buffer), "%Y-%m-%d %H:%M:%S", &timeinfo);
  return String(buffer);
}

int getCurrentHour() {
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) return -1;
  return timeinfo.tm_hour;
}

bool isTimeValid() {
  struct tm timeinfo;
  return getLocalTime(&timeinfo);
}

#endif // TIME_MANAGER_H