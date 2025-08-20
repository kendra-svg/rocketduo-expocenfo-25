/*
 * audio_player.h
 */

#ifndef AUDIO_PLAYER_H
#define AUDIO_PLAYER_H

#include "config.h"
#include "led_controller.h"
#include "buzzer_controller.h"
#include "server_communication.h"

// Enum para tipos de audio (simplificado)
enum AudioType {
  AUDIO_REMINDER,
  AUDIO_WATER,
  AUDIO_EMERGENCY,
  AUDIO_STARTUP,
  AUDIO_TEST
};

// FUNCIÓN PRINCIPAL - Enciende LEDs y reproduce audio en servidor
bool playAudio(AudioType type, String audioUrl = "", String mensaje = "", String medicamento = "") {
  Serial.println("Iniciando reproducción...");
  
  allLEDsOn();
  Serial.println("Todas las luces encendidas");
  
  switch(type) {
    case AUDIO_REMINDER:
      executePattern(PATTERN_REMINDER);
      playBuzzerTone(TONE_REMINDER);
      break;
    case AUDIO_WATER:
      executePattern(PATTERN_WATER);
      playBuzzerTone(TONE_WATER);
      break;
    case AUDIO_EMERGENCY:
      executePattern(PATTERN_EMERGENCY);
      playBuzzerTone(TONE_EMERGENCY);
      break;
    case AUDIO_STARTUP:
      executePattern(PATTERN_SYSTEM_READY);
      playBuzzerTone(TONE_WELCOME);
      break;
    case AUDIO_TEST:
      executePattern(PATTERN_AUDIO_PLAYING);
      playBuzzerTone(TONE_TEST);
      break;
      
    bool audioSuccess = sendPlayAudioCommand(audioUrl, mensaje, medicamento);

  }
  
  bool audioSuccess = false;
  if (audioUrl.length() > 0) {
    audioSuccess = sendPlayAudioCommand(audioUrl, mensaje, medicamento);
    if (audioSuccess) {
      Serial.println("Audio enviado al servidor para reproducción");
    } else {
      Serial.println("Error enviando audio al servidor");
    }
  } else {
    Serial.println("No hay URL de audio, solo efectos visuales");
    audioSuccess = true; // Considerar exitoso si solo son efectos
  }
  
  return audioSuccess;
}

// Wrappers para mantener compatibilidad
bool playReminderAudio(String audioUrl, String mensaje, String medicamento) {
  Serial.println("💊 Reproduciendo recordatorio de medicamento:");
  Serial.println("   👤 Para: " + (mensaje.length() > 0 ? mensaje.substring(0, mensaje.indexOf(',')) : "Usuario"));
  Serial.println("   💊 Medicamento: " + medicamento);
  Serial.println("   🔗 Audio URL: " + audioUrl.substring(0, 50) + "...");
  
  return playAudio(AUDIO_REMINDER, audioUrl, mensaje, medicamento);
}

bool playWaterReminderAudio() {
  Serial.println("💧 Reproduciendo recordatorio de agua");
  return playAudio(AUDIO_WATER, "", MSG_WATER_REMINDER, "");
}

bool playEmergencyAudio(String eventType) {
  Serial.println("🚨 Reproduciendo alerta de emergencia: " + eventType);
  return playAudio(AUDIO_EMERGENCY);
}

bool playSystemStartupAudio() {
  Serial.println("🚀 Reproduciendo audio de inicio del sistema");
  return playAudio(AUDIO_STARTUP);
}

bool playTestAudio() {
  Serial.println("🧪 Reproduciendo audio de prueba");
  return playAudio(AUDIO_TEST);
}

// Funciones específicas
bool playMedicineReminder(String audioUrl, String mensaje, String medicamento) {
  return playReminderAudio(audioUrl, mensaje, medicamento);
}

bool playTemperatureAlert(float temperature, bool isHot) {
  Serial.print("🌡️ Alerta de temperatura: ");
  Serial.print(temperature, 1);
  Serial.println(isHot ? "°C (ALTA)" : "°C (BAJA)");
  
  executePattern(PATTERN_TEMPERATURE, isHot);
  playBuzzerTone(isHot ? TONE_TEMP_HIGH : TONE_TEMP_LOW);
  return true;
}

void stopAllAudio() {
  allLEDsOff();
  silenceBuzzer();
  Serial.println("🔇 Audio y efectos detenidos");
}

bool isAnyAudioPlaying() {
  // En esta versión simplificada, consideramos que no hay audio reproduciéndose
  // ya que se maneja en el servidor
  return false;
}

String getAudioSystemStatus() {
  if (systemStatus.wifiConnected) {
    return "Servidor Conectado";
  }
  return "Solo Efectos Locales";
}

void setSystemVolume(int volume) {
  // En esta versión, el volumen se maneja en el servidor
  Serial.println("🔊 Volumen manejado por servidor: " + String(volume) + "%");
}

#endif // AUDIO_PLAYER_H