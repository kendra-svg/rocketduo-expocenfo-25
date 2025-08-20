/*
 * config.h 
 */

#ifndef CONFIG_H
#define CONFIG_H

#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <time.h>
#include <Adafruit_NeoPixel.h>
#include <WiFiClientSecure.h>

// ===== DEBUG CONDICIONAL =====
#define DEBUG_MODE 1  // 0 = Sin debug, 1 = Debug básico

#if DEBUG_MODE > 0
  #define DEBUG_PRINT(x) Serial.println(x)
  #define DEBUG_PRINTF(x, y) Serial.printf(x, y)
#else
  #define DEBUG_PRINT(x)
  #define DEBUG_PRINTF(x, y)
#endif

// ===== CONFIGURACIÓN DE RED =====
const char* WIFI_SSID PROGMEM = "LIB-0971396";        // ← CAMBIAR AQUÍ
const char* WIFI_PASSWORD PROGMEM = "cspaT5h9dnga"; // ← CAMBIAR AQUÍ
const char* SERVER_URL PROGMEM = "http://192.168.50.249:5000/api/esp32"; // ← CAMBIAR IP Y PUERTO

// ===== PINES DEL IDEABOARD =====
// Basado en el pinout del IdeaBoard
#define LED_RED_PIN     32    // Pin digital para LED rojo
#define LED_GREEN_PIN   5    // Pin digital para LED verde  
#define LED_BLUE_PIN    23   // Pin digital para LED azul
#define LED_YELLOW_PIN  18   // Pin digital para LED amarillo
#define RGB_LED_PIN     2    // LED RGB integrado (WS2812B)
#define RGB_LED_COUNT   1

#define BUTTON_RED_PIN    32  // Botón emergencia médica
#define BUTTON_BLUE_PIN   33  // Botón tristeza/soledad
#define BUTTON_YELLOW_PIN 19  // Botón hambre

#define TEMP_SENSOR_PIN 22    // Sensor de temperatura (analógico)
#define BUZZER_PIN      21    // Buzzer pasivo

// ===== CONFIGURACIONES DE TIEMPO =====
#define NTP_SERVER1     "pool.ntp.org"
#define NTP_SERVER2     "time.nist.gov"
#define GMT_OFFSET_SEC  -21600  // Costa Rica UTC-6 (cambiar según tu zona)
#define DAYLIGHT_OFFSET 0

// ===== CONFIGURACIONES DE SENSORES =====
#define TEMP_MIN        18.0
#define TEMP_MAX        28.0
#define TEMP_CHECK_INTERVAL 300000  // 5 minutos

// ===== CONFIGURACIONES DE RECORDATORIOS =====
#define MAX_REMINDERS   10
#define WATER_INTERVAL  7200000  // 2 horas
#define WATER_START_HOUR 8
#define WATER_END_HOUR   18

// ===== CONFIGURACIONES DE CONECTIVIDAD =====
#define WIFI_TIMEOUT    20000   // 20 segundos
#define HTTP_TIMEOUT    15000   // 15 segundos

// ===== STRINGS ESENCIALES =====
const char MSG_WIFI_CONNECTING[] PROGMEM = "Conectando WiFi...";
const char MSG_WIFI_CONNECTED[] PROGMEM = "WiFi conectado";
const char MSG_WIFI_FAILED[] PROGMEM = "Error WiFi";
const char MSG_TEMP_LOW[] PROGMEM = "Temperatura baja, use abrigo";
const char MSG_TEMP_HIGH[] PROGMEM = "Temperatura alta, hidrátese";
const char MSG_WATER_REMINDER[] PROGMEM = "Hora de tomar agua";

// ===== ENDPOINTS =====
const char ENDPOINT_CONFIG[] PROGMEM = "/config";
const char ENDPOINT_EVENT[] PROGMEM = "/evento";
const char ENDPOINT_TEMP[] PROGMEM = "/temperatura";
const char ENDPOINT_WATER[] PROGMEM = "/agua";
const char ENDPOINT_PLAY_AUDIO[] PROGMEM = "/play-audio"; // ← Nuevo endpoint

// ===== ESTRUCTURAS SIMPLIFICADAS =====
struct Reminder {
  String id;
  String quien;
  String hora;
  String medicamento;
  String mensaje;
  String audioUrl;
  String frecuencia;
  bool activo;
  
  // Constructor por defecto
  Reminder() : activo(false) {}
  
  // Constructor con parámetros
  Reminder(String _id, String _quien, String _hora, String _medicamento, 
           String _mensaje, String _audioUrl, String _frecuencia, bool _activo) :
    id(_id), quien(_quien), hora(_hora), medicamento(_medicamento),
    mensaje(_mensaje), audioUrl(_audioUrl), frecuencia(_frecuencia), activo(_activo) {}
};

struct SystemStatus {
  bool wifiConnected;
  float lastTemperature;
  unsigned long lastWaterReminder;
  int activeReminders;
  bool systemReady;
  String lastError;
};

// ===== CÓDIGOS DE ERROR =====
#define ERROR_WIFI      1001
#define ERROR_SERVER    1003
#define ERROR_AUDIO     1004
#define ERROR_TEMP      1005

// ===== DECLARACIONES GLOBALES =====
extern Reminder reminders[MAX_REMINDERS];
extern SystemStatus systemStatus;
extern Adafruit_NeoPixel rgbLed;
extern HTTPClient http;

// ===== ENUMS =====
enum PatternType {
  PATTERN_REMINDER,
  PATTERN_EMERGENCY, 
  PATTERN_SADNESS,
  PATTERN_HUNGER,
  PATTERN_TEMPERATURE,
  PATTERN_WATER,
  PATTERN_SYSTEM_READY,
  PATTERN_ERROR,
  PATTERN_AUDIO_PLAYING  // ← Nuevo
};

enum ToneType {
  TONE_WELCOME,
  TONE_REMINDER, 
  TONE_EMERGENCY,
  TONE_SUCCESS,
  TONE_ERROR,
  TONE_WATER,
  TONE_TEMP_HIGH,
  TONE_TEMP_LOW,
  TONE_BUTTON_RED,
  TONE_BUTTON_BLUE,
  TONE_BUTTON_YELLOW,
  TONE_TEST
};

// ===== DECLARACIONES FORWARD DE FUNCIONES =====
extern void executePattern(PatternType type, bool isHot = false);
extern void playBuzzerTone(ToneType type);
extern void setRGBColor(uint8_t red, uint8_t green, uint8_t blue);
extern void allLEDsOff();

// ===== FUNCIONES DE UTILIDAD =====

// Función para mostrar información del sistema
void printSystemInfo() {
  DEBUG_PRINT("=== INFORMACIÓN DEL SISTEMA ===");
  DEBUG_PRINT("Chip: " + String(ESP.getChipModel()));
  DEBUG_PRINT("Frecuencia CPU: " + String(ESP.getCpuFreqMHz()) + " MHz");
  DEBUG_PRINT("Memoria libre: " + String(ESP.getFreeHeap()) + " bytes");
  DEBUG_PRINT("Flash: " + String(ESP.getFlashChipSize()) + " bytes");
  DEBUG_PRINT("MAC WiFi: " + WiFi.macAddress());
  DEBUG_PRINT("Configuración:");
  DEBUG_PRINT("  SSID objetivo: " + String(WIFI_SSID));
  DEBUG_PRINT("  Servidor: " + String(SERVER_URL));
  DEBUG_PRINT("==============================");
}

// Función para verificar configuración
bool verifyConfiguration() {
  bool configOK = true;
  
  DEBUG_PRINT("🔍 Verificando configuración...");
  
  // Verificar SSID
  if (String(WIFI_SSID) == "TU_WIFI_SSID") {
    DEBUG_PRINT("❌ SSID no configurado");
    configOK = false;
  }
  
  // Verificar contraseña
  if (String(WIFI_PASSWORD) == "TU_WIFI_PASSWORD") {
    DEBUG_PRINT("❌ Contraseña WiFi no configurada");
    configOK = false;
  }
  
  // Verificar servidor
  if (String(SERVER_URL).indexOf("192.168.1.100") >= 0) {
    DEBUG_PRINT("⚠️ IP del servidor no cambiada (usando IP por defecto)");
  }
  
  if (configOK) {
    DEBUG_PRINT("✅ Configuración verificada");
  } else {
    DEBUG_PRINT("❌ Configuración incompleta - revisar config.h");
  }
  
  return configOK;
}

// ===== DECLARACIONES FORWARD DE FUNCIONES =====
extern bool loadRemindersFromServer();
extern bool testServerConnection();
extern void serverDiagnostic();
extern bool sendSystemStatus();

extern void connectWiFi();
extern void checkWiFiConnection();
extern bool isWiFiConnected();
extern String getWiFiIP();

extern void initTimeManager();
extern String getCurrentTime();
extern String getFormattedDateTime();
extern bool isTimeValid();

extern void checkReminders();
extern void checkWaterReminder();

extern void initTemperatureSensor();
extern void checkTemperature();

extern void initButtons();
extern void handleButtons();

extern void initLEDs();
extern void initBuzzer();

// ===== MACROS DE CONVENIENCIA =====
#define WIFI_IS_CONNECTED() (WiFi.status() == WL_CONNECTED)
#define SYSTEM_IS_READY() (systemStatus.systemReady && WIFI_IS_CONNECTED())

// ===== CONFIGURACIÓN DE MEMORIA =====
#define JSON_BUFFER_SIZE 2048    // Tamaño buffer JSON

#endif // CONFIG_H