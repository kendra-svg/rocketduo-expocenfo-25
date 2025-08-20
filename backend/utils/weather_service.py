import os
import requests

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = os.getenv("OPENWEATHER_BASE_URL", "https://api.openweathermap.org/data/2.5/weather")

def obtener_temp_actual(lat: float, lon: float, unidades: str = "metric", lang: str = "es") -> float:
    """Devuelve la temperatura actual (°C) usando OpenWeather."""
    if not API_KEY:
        raise RuntimeError("Falta OPENWEATHER_API_KEY en el entorno")
    params = {"lat": lat, "lon": lon, "appid": API_KEY, "units": unidades, "lang": lang}
    r = requests.get(BASE_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    return float(data["main"]["temp"])
