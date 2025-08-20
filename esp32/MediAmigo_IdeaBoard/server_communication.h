/*
 * server_communication.h
 */

#ifndef SERVER_COMMUNICATION_H
#define SERVER_COMMUNICATION_H

#include "config.h"
#include "wifi_manager.h"

extern String getFormattedTime();

// ===== FUNCIÓN NUEVA - Enviar comando de reproducción de audio al servidor =====
bool sendPlayAudioCommand(String audioUrl, String mensaje, String medicamento) {
  if (!isWiFiConnected()) {
    DEBUG_PRINT("WiFi no conectado");
    return false;
  }
  
  String url = String(SERVER_URL) + String(ENDPOINT_PLAY_AUDIO);
  
  HTTPClient http;
  WiFiClient client;
  
  http.begin(client, url);
  http.setTimeout(HTTP_TIMEOUT);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("Connection", "close");
  
  // Crear JSON con datos del audio
  DynamicJsonDocument doc(1024);
  doc["audio_url"] = audioUrl;
  doc["mensaje"] = mensaje;
  doc["medicamento"] = medicamento;
  doc["dispositivo"] = "MediAmigo_ESP32";
  doc["timestamp"] = getFormattedTime();
  doc["accion"] = "reproducir_audio";
  
  String jsonData;
  serializeJson(doc, jsonData);
  
  DEBUG_PRINT(String("🎵 Enviando comando de audio: ") + url);
  DEBUG_PRINT(String("📊 Datos: ") + jsonData);
  
  unsigned long startTime = millis();
  int httpCode = http.POST(jsonData);
  unsigned long requestTime = millis() - startTime;
  
  String response = http.getString();
  http.end();
  
  DEBUG_PRINT(String("📻 Código HTTP: ") + String(httpCode));
  DEBUG_PRINT(String("⏱️ Tiempo respuesta: ") + String(requestTime) + " ms");
  DEBUG_PRINT(String("📝 Respuesta: ") + response.substring(0, 100));
  
  if (httpCode == 200) {
    DEBUG_PRINT("Comando de audio enviado exitosamente");
    return true;
  } else {
    DEBUG_PRINT(String("Error enviando comando de audio: ") + String(httpCode));
    return false;
  }
}

// ===== FUNCIÓN PARA CARGAR RECORDATORIOS =====
bool loadRemindersFromServer() {
  if (!isWiFiConnected()) {
    DEBUG_PRINT("WiFi no conectado");
    return false;
  }
  
  String url = String(SERVER_URL) + String(ENDPOINT_CONFIG);
  
  HTTPClient http;
  WiFiClient client;
  
  http.begin(client, url);
  http.setTimeout(HTTP_TIMEOUT);
  http.addHeader("User-Agent", "ESP32-MediAmigo");
  http.addHeader("Connection", "close");
  http.addHeader("Accept", "application/json");
  
  DEBUG_PRINT(String("📡 Consultando servidor: ") + url);
  
  unsigned long startTime = millis();
  int httpCode = http.GET();
  unsigned long requestTime = millis() - startTime;
  
  DEBUG_PRINT(String("📊 Código HTTP: ") + String(httpCode));
  DEBUG_PRINT(String("⏱️ Tiempo respuesta: ") + String(requestTime) + " ms");
  
  if (httpCode < 0) {
    DEBUG_PRINT(String("Error conexión HTTP: ") + http.errorToString(httpCode));
    http.end();
    return false;
  }
  
  if (httpCode != 200) {
    DEBUG_PRINT(String("Error HTTP: ") + String(httpCode));
    String response = http.getString();
    DEBUG_PRINT(String("Respuesta: ") + response.substring(0, 100));
    http.end();
    return false;
  }
  
  String response = http.getString();
  http.end();
  
  DEBUG_PRINT(String("Respuesta recibida (") + String(response.length()) + " bytes)");
  #if DEBUG_MODE > 0
    DEBUG_PRINT(String("JSON: ") + response.substring(0, 200) + "...");
  #endif
  
  if (response.length() == 0) {
    DEBUG_PRINT("Respuesta vacía");
    return false;
  }
  
  // Parsear JSON
  DynamicJsonDocument doc(4096);
  
  DeserializationError error = deserializeJson(doc, response);
  if (error) {
    DEBUG_PRINT(String("Error parseando JSON: ") + String(error.c_str()));
    return false;
  }
  
  DEBUG_PRINT("JSON parseado correctamente");
  
  // Limpiar recordatorios anteriores
  for (int i = 0; i < MAX_REMINDERS; i++) {
    reminders[i] = Reminder();
  }
  systemStatus.activeReminders = 0;
  
  // Procesar respuesta JSON
  if (doc.is<JsonArray>()) {
    // Array de recordatorios
    JsonArray recordatorios = doc.as<JsonArray>();
    int count = 0;
    
    for (JsonObject recordatorio : recordatorios) {
      if (count >= MAX_REMINDERS) break;
      
      reminders[count].id = recordatorio["id"].as<String>();
      reminders[count].quien = recordatorio["quien"].as<String>();
      reminders[count].hora = recordatorio["hora"].as<String>();
      reminders[count].medicamento = recordatorio["medicamento"].as<String>();
      reminders[count].mensaje = recordatorio["mensaje"].as<String>();
      reminders[count].audioUrl = recordatorio["audio_url"].as<String>();
      reminders[count].activo = true;
      
      count++;
    }
    systemStatus.activeReminders = count;
    
  } else if (doc.containsKey("recordatorios")) {
    // Objeto con campo "recordatorios"
    JsonArray recordatorios = doc["recordatorios"];
    int count = 0;
    
    for (JsonObject recordatorio : recordatorios) {
      if (count >= MAX_REMINDERS) break;
      
      reminders[count].id = recordatorio["id"].as<String>();
      reminders[count].quien = recordatorio["quien"].as<String>();
      reminders[count].hora = recordatorio["hora"].as<String>();
      reminders[count].medicamento = recordatorio["medicamento"].as<String>();
      reminders[count].mensaje = recordatorio["mensaje"].as<String>();
      reminders[count].audioUrl = recordatorio["audio_url"].as<String>();
      reminders[count].activo = true;
      
      count++;
    }
    systemStatus.activeReminders = count;
    
  } else if (doc.containsKey("id")) {
    // Objeto individual
    reminders[0].id = doc["id"].as<String>();
    reminders[0].quien = doc["quien"].as<String>();
    reminders[0].hora = doc["hora"].as<String>();
    reminders[0].medicamento = doc["medicamento"].as<String>();
    reminders[0].mensaje = doc["mensaje"].as<String>();
    reminders[0].audioUrl = doc["audio_url"].as<String>();
    reminders[0].activo = true;
    
    systemStatus.activeReminders = 1;
    
    DEBUG_PRINT(String("Recordatorio cargado: ") + reminders[0].quien + 
                String(" - ") + reminders[0].medicamento + 
                String(" a las ") + reminders[0].hora);
  }
  
  DEBUG_PRINT(String("📊 Total recordatorios cargados: ") + String(systemStatus.activeReminders));
  
  return systemStatus.activeReminders > 0;
}

// ===== FUNCIÓN DE PRUEBA DE CONECTIVIDAD =====
bool testServerConnection() {
  if (!isWiFiConnected()) return false;
  
  String url = String(SERVER_URL) + "/test";
  
  HTTPClient http;
  WiFiClient client;
  
  http.begin(client, url);
  http.setTimeout(5000);
  
  DEBUG_PRINT(String("🔍 Probando servidor: ") + url);
  
  int httpCode = http.GET();
  String response = http.getString();
  http.end();
  
  DEBUG_PRINT(String("Test - Código: ") + String(httpCode));
  DEBUG_PRINT(String("Test - Respuesta: ") + response);
  
  return (httpCode == 200);
}

// ===== FUNCIONES DE EVENTOS =====
bool sendEmergencyEvent(String tipoEvento) {
  if (!isWiFiConnected()) return false;
  
  String url = String(SERVER_URL) + String(ENDPOINT_EVENT);
  
  HTTPClient http;
  WiFiClient client;
  
  http.begin(client, url);
  http.setTimeout(HTTP_TIMEOUT);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("Connection", "close");
  
  DynamicJsonDocument doc(512);
  doc["tipo"] = "boton_presionado";
  doc["evento"] = tipoEvento;
  doc["dispositivo"] = "MediAmigo_ESP32";
  doc["timestamp"] = getFormattedTime();
  
  String jsonData;
  serializeJson(doc, jsonData);
  
  int code = http.POST(jsonData);
  http.end();
  
  DEBUG_PRINT(String("Evento enviado: ") + tipoEvento + String(" - Código: ") + String(code));
  
  return (code == 200);
}

bool sendTemperatureData(float temperature) {
  if (!isWiFiConnected()) return false;
  
  String url = String(SERVER_URL) + String(ENDPOINT_TEMP);
  
  HTTPClient http;
  WiFiClient client;
  
  http.begin(client, url);
  http.setTimeout(HTTP_TIMEOUT);
  http.addHeader("Content-Type", "application/json");
  
  DynamicJsonDocument doc(512);
  doc["tipo"] = "temperatura";
  doc["valor"] = temperature;
  doc["dispositivo"] = "MediAmigo_ESP32";
  doc["timestamp"] = getFormattedTime();
  
  String jsonData;
  serializeJson(doc, jsonData);
  
  int code = http.POST(jsonData);
  http.end();
  
  return (code == 200);
}

bool sendWaterReminderEvent() {
  if (!isWiFiConnected()) return false;
  
  String url = String(SERVER_URL) + "/agua";
  
  HTTPClient http;
  WiFiClient client;
  
  http.begin(client, url);
  http.setTimeout(HTTP_TIMEOUT);
  http.addHeader("Content-Type", "application/json");
  
  DynamicJsonDocument doc(512);
  doc["tipo"] = "recordatorio_agua";
  doc["dispositivo"] = "MediAmigo_ESP32";
  doc["timestamp"] = getFormattedTime();
  
  String jsonData;
  serializeJson(doc, jsonData);
  
  int code = http.POST(jsonData);
  http.end();
  
  return (code == 200);
}

bool sendSystemStatus() {
  if (!isWiFiConnected()) return false;
  
  String url = String(SERVER_URL) + "/estado";
  HTTPClient http;
  WiFiClient client;
  
  http.begin(client, url);
  http.setTimeout(HTTP_TIMEOUT);
  
  DynamicJsonDocument doc(512);
  doc["tipo"] = "estado_sistema";
  doc["dispositivo"] = "MediAmigo_ESP32";
  doc["wifi_conectado"] = systemStatus.wifiConnected;
  doc["temperatura_actual"] = systemStatus.lastTemperature;
  doc["recordatorios_activos"] = systemStatus.activeReminders;
  doc["sistema_listo"] = systemStatus.systemReady;
  doc["timestamp"] = getFormattedTime();
  
  String jsonData;
  serializeJson(doc, jsonData);
  
  http.addHeader("Content-Type", "application/json");
  int code = http.POST(jsonData);
  http.end();
  
  return (code == 200);
}

// ===== FUNCIÓN DE DIAGNÓSTICO DEL SERVIDOR =====
void serverDiagnostic() {
  DEBUG_PRINT("=== DIAGNÓSTICO SERVIDOR ===");
  DEBUG_PRINT(String("URL base: ") + String(SERVER_URL));
  DEBUG_PRINT(String("WiFi conectado: ") + (isWiFiConnected() ? "SÍ" : "NO"));
  
  if (isWiFiConnected()) {
    DEBUG_PRINT(String("IP local: ") + WiFi.localIP().toString());
    DEBUG_PRINT(String("RSSI: ") + String(WiFi.RSSI()) + " dBm");
    
    // Probar conectividad
    bool serverOk = testServerConnection();
    DEBUG_PRINT(String("Servidor accesible: ") + (serverOk ? "SÍ" : "NO"));
    
    if (serverOk) {
      DEBUG_PRINT("Comunicación servidor OK");
    } else {
      DEBUG_PRINT("Problema comunicación servidor");
      DEBUG_PRINT("Verificar IP/Puerto en config.h");
    }
  }
  DEBUG_PRINT("============================");
}

// Función para enviar alertas de temperatura
bool sendTemperatureAlert(float temperature, String tipo) {
  if (!isWiFiConnected()) return false;
  
  String url = String(SERVER_URL) + String(ENDPOINT_TEMP);
  HTTPClient http;
  WiFiClient client;
  
  http.begin(client, url);
  http.setTimeout(HTTP_TIMEOUT);
  
  DynamicJsonDocument doc(512);
  doc["tipo"] = "alerta_temperatura";
  doc["subtipo"] = tipo;
  doc["valor"] = temperature;
  doc["dispositivo"] = "MediAmigo_ESP32";
  doc["timestamp"] = getFormattedTime();
  
  String jsonData;
  serializeJson(doc, jsonData);
  
  http.addHeader("Content-Type", "application/json");
  int code = http.POST(jsonData);
  http.end();
  
  return (code == 200);
}

#endif // SERVER_COMMUNICATION_H