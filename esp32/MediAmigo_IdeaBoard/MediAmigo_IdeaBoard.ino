/*
 * MediAmigo IdeaBoard ESP32
 * Sistema de recordatorios médicos solo con LEDs y audio
 * Versión: 1
 */

#include "config.h"
#include "wifi_manager.h"
#include "led_controller.h"
#include "button_handler.h"
#include "temperature_sensor.h"
#include "buzzer_controller.h"
#include "audio_player.h"
#include "server_communication.h"
#include "reminder_manager.h"
#include "time_manager.h"

// Variables globales
Adafruit_NeoPixel rgbLed(RGB_LED_COUNT, RGB_LED_PIN, NEO_GRB + NEO_KHZ800);
HTTPClient http;
Reminder reminders[MAX_REMINDERS];
SystemStatus systemStatus = {false, 0.0, 0, 0, false, ""};

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("=== MediAmigo v1.0 ===");
  
  // Verificar configuración ANTES de inicializar
  if (!verifyConfiguration()) {
    Serial.println("CONFIGURACIÓN INCOMPLETA");
    Serial.println("Editar config.h con tus datos:");
    Serial.println("   - WIFI_SSID y WIFI_PASSWORD");
    Serial.println("   - SERVER_URL (IP de tu servidor)");
    Serial.println("");
  }
  
  // Mostrar información del sistema
  printSystemInfo();
  
  // Inicializar componentes básicos
  initLEDs();
  initButtons();
  initBuzzer();
  initTemperatureSensor();
  
  // Secuencia de bienvenida
  executePattern(PATTERN_SYSTEM_READY);
  playBuzzerTone(TONE_WELCOME);
  
  // === CONECTIVIDAD ===
  connectWiFi();
  if (systemStatus.wifiConnected) {
    initTimeManager();
    serverDiagnostic();
  }
  
  // === CARGAR RECORDATORIOS ===
  if (systemStatus.wifiConnected) {
    Serial.println("Cargando recordatorios del servidor...");
    bool loaded = loadRemindersFromServer();
    if (!loaded) {
      Serial.println("Primera carga falló, reintentando en 3 segundos...");
      delay(3000);
      loaded = loadRemindersFromServer();
      if (!loaded) {
        Serial.println("No se pudieron cargar recordatorios");
        Serial.println("Verificar que el servidor esté funcionando");
      }
    }
  } else {
    Serial.println("Sin WiFi - No se pueden cargar recordatorios");
    systemStatus.activeReminders = 0;
  }
  
  // === SISTEMA LISTO ===
  systemStatus.systemReady = true;
  
  Serial.println("");
  Serial.println("SISTEMA LISTO PARA FUNCIONAR");
  Serial.println("");
  Serial.println("COMANDOS DISPONIBLES:");
  Serial.println("  'status'     - Ver estado completo");
  Serial.println("  'test'       - Probar recordatorio ahora");
  Serial.println("  'refresh'    - Recargar recordatorios");
  Serial.println("  'ping'       - Probar conectividad servidor");
  Serial.println("  'wifi'       - Diagnóstico WiFi");
  Serial.println("  'time'       - Ver información de tiempo");
  Serial.println("  'config'     - Verificar configuración");
  Serial.println("  'help'       - Mostrar ayuda completa");
  Serial.println("");
  
  // Patrón final de sistema listo
  delay(1000);
  executePattern(PATTERN_SYSTEM_READY);
}

void loop() {
  static unsigned long lastReminderCheck = 0;
  static unsigned long lastTempCheck = 0;
  static unsigned long lastConnCheck = 0;
  static unsigned long lastReport = 0;
  
  unsigned long now = millis();
  
  // === VERIFICACIONES CRÍTICAS (cada ciclo) ===
  handleButtons();
  if (Serial.available()) handleSerialCommand();
  
  // === VERIFICACIONES TEMPORIZADAS ===
  
  // Recordatorios cada minuto
  if (now - lastReminderCheck >= 60000) {
    if (systemStatus.systemReady) {
      checkReminders();
      checkWaterReminder();
    }
    lastReminderCheck = now;
  }
  
  // Temperatura cada 5 minutos
  if (now - lastTempCheck >= TEMP_CHECK_INTERVAL) {
    checkTemperature();
    lastTempCheck = now;
  }
  
  // Conectividad cada 30 segundos
  if (now - lastConnCheck >= 30000) {
    checkWiFiConnection();
    lastConnCheck = now;
  }
  
  // Reporte de estado cada 5 minutos
  if (now - lastReport >= 300000) {
    printSystemStatus();
    if (systemStatus.wifiConnected) sendSystemStatus();
    lastReport = now;
  }
  
  delay(100);
}

// ===== FUNCIONES AUXILIARES =====

void printSystemStatus() {
  Serial.println("");
  Serial.println("=== ESTADO DEL SISTEMA ===");
  Serial.print("Sistema: "); 
  Serial.println(systemStatus.systemReady ? "LISTO" : "INICIALIZANDO");
  
  Serial.print("📡 WiFi: "); 
  if (systemStatus.wifiConnected) {
    Serial.print("CONECTADO (");
    Serial.print(getWiFiIP());
    Serial.print(", RSSI: ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm)");
  } else {
    Serial.println("DESCONECTADO");
  }
  
  Serial.print("Hora: "); 
  Serial.println(getFormattedDateTime());
  
  Serial.print("Temperatura: "); 
  Serial.print(systemStatus.lastTemperature, 1);
  Serial.println("°C");
  
  Serial.print("Recordatorios: "); 
  Serial.println(systemStatus.activeReminders);
  
  if (systemStatus.lastError.length() > 0) {
    Serial.print("Último error: ");
    Serial.println(systemStatus.lastError);
  }
  
  Serial.print("Memoria libre: ");
  Serial.print(ESP.getFreeHeap());
  Serial.println(" bytes");
  
  Serial.print("Uptime: ");
  Serial.print(millis() / 1000);
  Serial.println(" segundos");
  
  Serial.println("==========================");
  Serial.println("");
}

// COMANDOS SERIALES
void handleSerialCommand() {
  String cmd = Serial.readStringUntil('\n');
  cmd.trim();
  cmd.toLowerCase();
  
  Serial.print("Comando: ");
  Serial.println(cmd);
  
  if (cmd == "status") {
    printSystemStatus();
    
  } else if (cmd == "test") {
    testReminderNow();
    
  } else if (cmd == "refresh") {
    Serial.println("Recargando recordatorios...");
    bool success = loadRemindersFromServer();
    Serial.println(success ? "Recordatorios actualizados" : "Error recargando");
    
  } else if (cmd == "ping") {
    Serial.println("Probando servidor...");
    bool ok = testServerConnection();
    Serial.println(ok ? "Servidor accesible" : "Servidor no responde");
    
  } else if (cmd == "wifi") {
    wifiDiagnostic();
    
  } else if (cmd == "time") {
    showTimeInfo();
    
  } else if (cmd == "config") {
    verifyConfiguration();
    
  } else if (cmd == "help") {
    showHelp();
    
  } else if (cmd == "reboot") {
    Serial.println("🔄 Reiniciando sistema...");
    delay(1000);
    ESP.restart();
    
  } else {
    Serial.println("Comando no reconocido. Usa 'help' para ver comandos disponibles.");
  }
}

void testReminderNow() {
  if (systemStatus.activeReminders == 0) {
    Serial.println("No hay recordatorios cargados");
    Serial.println("Usa 'refresh' para cargar del servidor");
    return;
  }
  
  Serial.println("Probando recordatorio...");
  
  // Usar el primer recordatorio activo
  for (int i = 0; i < MAX_REMINDERS; i++) {
    if (reminders[i].activo) {
      Serial.println("Recordatorio de prueba:");
      Serial.print("  ");
      Serial.println(reminders[i].quien);
      Serial.print("  ");
      Serial.println(reminders[i].medicamento);
      Serial.print("  ");
      Serial.println(reminders[i].mensaje);
      
      // Ejecutar patrón LED completo y reproducir audio en servidor
      bool success = playReminderAudio(
        reminders[i].audioUrl,
        reminders[i].mensaje,
        reminders[i].medicamento
      );
      
      Serial.println(success ? "Prueba completada" : "Error en prueba");
      break;
    }
  }
}

void wifiDiagnostic() {
  Serial.println("=== DIAGNÓSTICO WIFI ===");
  Serial.print("SSID configurado: ");
  Serial.println(String(WIFI_SSID));
  Serial.print("Estado: ");
  Serial.println(WIFI_IS_CONNECTED() ? "CONECTADO" : "DESCONECTADO");
  
  if (WIFI_IS_CONNECTED()) {
    Serial.print("IP: ");
    Serial.println(WiFi.localIP().toString());
    Serial.print("Gateway: ");
    Serial.println(WiFi.gatewayIP().toString());
    Serial.print("DNS: ");
    Serial.println(WiFi.dnsIP().toString());
    Serial.print("RSSI: ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
    Serial.print("Calidad: ");
    Serial.println(getWiFiQuality());
  }
  Serial.println("========================");
}

String getWiFiQuality() {
  int rssi = WiFi.RSSI();
  if (rssi >= -50) return "Excelente";
  if (rssi >= -60) return "Buena";
  if (rssi >= -70) return "Regular";
  if (rssi >= -80) return "Débil";
  return "Muy débil";
}

void showTimeInfo() {
  Serial.println("=== INFORMACIÓN DE TIEMPO ===");
  Serial.print("Hora actual: ");
  Serial.println(getCurrentTime());
  Serial.print("Fecha completa: ");
  Serial.println(getFormattedDateTime());
  Serial.print("Zona horaria: UTC");
  Serial.println(String(GMT_OFFSET_SEC / 3600));
  Serial.print("NTP sincronizado: ");
  Serial.println(String(isTimeValid() ? "SÍ" : "NO"));
  Serial.println("==============================");
}

void showHelp() {
  Serial.println("");
  Serial.println("=== AYUDA - COMANDOS DISPONIBLES ===");
  Serial.println("INFORMACIÓN:");
  Serial.println("  status    - Estado completo del sistema");
  Serial.println("  wifi      - Diagnóstico WiFi detallado");
  Serial.println("  time      - Información de fecha/hora");
  Serial.println("  config    - Verificar configuración");
  Serial.println("");
  Serial.println("PRUEBAS:");
  Serial.println("  test      - Probar recordatorio actual");
  Serial.println("  ping      - Probar conectividad servidor");
  Serial.println("");
  Serial.println("ACCIONES:");
  Serial.println("  refresh   - Recargar recordatorios");
  Serial.println("  reboot    - Reiniciar sistema");
  Serial.println("");
  Serial.println("AYUDA:");
  Serial.println("  help      - Mostrar esta ayuda");
  Serial.println("====================================");
  Serial.println("");
}

void handleSystemError(int errorCode) {
  String errorMsg = "Error " + String(errorCode);
  systemStatus.lastError = errorMsg;
  
  executePattern(PATTERN_ERROR);
  playBuzzerTone(TONE_ERROR);
  
  Serial.print(" ");
  Serial.println(errorMsg);
  
  switch (errorCode) {
    case ERROR_WIFI:
      Serial.println("Intentando reconectar WiFi...");
      connectWiFi();
      break;
    case ERROR_SERVER:
      Serial.println("Problema con servidor - verificar conectividad");
      break;
    case ERROR_AUDIO:
      Serial.println("Error de audio - verificar servidor");
      break;
  }
}