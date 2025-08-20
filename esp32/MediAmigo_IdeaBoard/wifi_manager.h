/*
 * wifi_manager.h - Gestión completa de WiFi
 */

#ifndef WIFI_MANAGER_H
#define WIFI_MANAGER_H

#include "config.h"
#include "led_controller.h"

void connectWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  Serial.print(F("Conectando WiFi..."));
  
  // LED amarillo parpadeando durante conexión
  setRGBColor(255, 255, 0);
  
  unsigned long startTime = millis();
  while (WiFi.status() != WL_CONNECTED && 
         millis() - startTime < WIFI_TIMEOUT) {
    
    digitalWrite(LED_YELLOW_PIN, !digitalRead(LED_YELLOW_PIN));
    delay(500);
    Serial.print(F("."));
  }
  
  digitalWrite(LED_YELLOW_PIN, LOW);
  
  if (WiFi.status() == WL_CONNECTED) {
    systemStatus.wifiConnected = true;
    setRGBColor(0, 255, 0); // Verde
    
    Serial.println();
    Serial.println(F("WiFi conectado"));
    Serial.print(F("IP: "));
    Serial.println(WiFi.localIP());
    Serial.print(F("RSSI: "));
    Serial.print(WiFi.RSSI());
    Serial.println(F(" dBm"));
    
    delay(2000);
    setRGBColor(0, 0, 0);
  } else {
    systemStatus.wifiConnected = false;
    setRGBColor(255, 0, 0); // Rojo
    
    Serial.println();
    Serial.println(F("Error WiFi"));
    
    // Parpadeo rojo de error
    for (int i = 0; i < 6; i++) {
      digitalWrite(LED_RED_PIN, HIGH);
      delay(200);
      digitalWrite(LED_RED_PIN, LOW);
      delay(200);
    }
    
    setRGBColor(0, 0, 0);
  }
}

void checkWiFiConnection() {
  if (WiFi.status() != WL_CONNECTED && systemStatus.wifiConnected) {
    Serial.println(F("⚠️ WiFi desconectado, reconectando..."));
    systemStatus.wifiConnected = false;
    connectWiFi();
  } else if (WiFi.status() == WL_CONNECTED && !systemStatus.wifiConnected) {
    systemStatus.wifiConnected = true;
    Serial.println(F("✅ WiFi reconectado"));
  }
}

bool isWiFiConnected() {
  return WiFi.status() == WL_CONNECTED;
}

int getWiFiRSSI() {
  return WiFi.RSSI();
}

String getWiFiIP() {
  return WiFi.localIP().toString();
}

void disconnectWiFi() {
  WiFi.disconnect();
  systemStatus.wifiConnected = false;
  Serial.println(F("📵 WiFi desconectado"));
}

#endif // WIFI_MANAGER_H