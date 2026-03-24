"""
Weather API Tool - OpenWeatherMap integration with mock fallback
"""

import os
import requests
from datetime import datetime
from typing import Dict, Any


class WeatherAPI:
    """Wraps OpenWeatherMap API. Falls back to mock data when key is unavailable."""

    BASE_URL = "https://api.openweathermap.org/data/2.5"

    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY", "")
        self.use_real = bool(self.api_key and self.api_key != "your_openweather_key_here")

    # ── public ────────────────────────────────────────────────────────────────

    def get_current_weather(self, city: str) -> Dict[str, Any]:
        """Return current weather for a city."""
        if self.use_real:
            return self._real_weather(city)
        return self._mock_weather(city)

    def get_forecast(self, city: str, days: int = 3) -> Dict[str, Any]:
        """Return a simple N-day forecast (real or mock)."""
        if self.use_real:
            return self._real_forecast(city, days)
        return self._mock_forecast(city, days)

    # ── real API ──────────────────────────────────────────────────────────────

    def _real_weather(self, city: str) -> Dict[str, Any]:
        try:
            url = f"{self.BASE_URL}/weather"
            params = {"q": city, "appid": self.api_key, "units": "metric"}
            resp = requests.get(url, params=params, timeout=8)
            resp.raise_for_status()
            d = resp.json()
            return {
                "success": True,
                "city": d.get("name", city),
                "country": d.get("sys", {}).get("country", ""),
                "temperature": d["main"]["temp"],
                "feels_like": d["main"]["feels_like"],
                "humidity": d["main"]["humidity"],
                "description": d["weather"][0]["description"].title(),
                "wind_speed": d["wind"]["speed"],
                "icon": d["weather"][0]["icon"],
                "source": "OpenWeatherMap",
            }
        except Exception as e:
            return {"success": False, "error": str(e), "city": city}

    def _real_forecast(self, city: str, days: int) -> Dict[str, Any]:
        try:
            url = f"{self.BASE_URL}/forecast"
            params = {"q": city, "appid": self.api_key, "units": "metric", "cnt": days * 8}
            resp = requests.get(url, params=params, timeout=8)
            resp.raise_for_status()
            data = resp.json()
            # summarize one entry per day
            daily: Dict[str, dict] = {}
            for item in data.get("list", []):
                day = item["dt_txt"].split()[0]
                if day not in daily:
                    daily[day] = {
                        "date": day,
                        "temp_min": item["main"]["temp_min"],
                        "temp_max": item["main"]["temp_max"],
                        "description": item["weather"][0]["description"].title(),
                        "humidity": item["main"]["humidity"],
                    }
            return {"success": True, "city": city, "forecast": list(daily.values())[:days]}
        except Exception as e:
            return {"success": False, "error": str(e), "city": city}

    # ── mock data ─────────────────────────────────────────────────────────────

    MOCK_DATA = {
        "chennai":    {"temperature": 34, "feels_like": 38, "humidity": 72, "description": "Mostly Sunny", "wind_speed": 3.2},
        "mumbai":     {"temperature": 30, "feels_like": 35, "humidity": 80, "description": "Partly Cloudy", "wind_speed": 4.1},
        "delhi":      {"temperature": 28, "feels_like": 31, "humidity": 55, "description": "Clear Sky",    "wind_speed": 2.8},
        "bangalore":  {"temperature": 24, "feels_like": 26, "humidity": 60, "description": "Light Rain",   "wind_speed": 3.5},
        "kolkata":    {"temperature": 32, "feels_like": 37, "humidity": 78, "description": "Thunderstorm", "wind_speed": 5.0},
        "hyderabad":  {"temperature": 36, "feels_like": 40, "humidity": 45, "description": "Hot & Sunny",  "wind_speed": 2.1},
        "coimbatore": {"temperature": 29, "feels_like": 33, "humidity": 68, "description": "Partly Cloudy","wind_speed": 3.0},
        "london":     {"temperature": 10, "feels_like": 7,  "humidity": 82, "description": "Overcast Clouds","wind_speed": 6.5},
        "new york":   {"temperature": 15, "feels_like": 12, "humidity": 65, "description": "Sunny",        "wind_speed": 4.3},
    }

    def _mock_weather(self, city: str) -> Dict[str, Any]:
        key = city.lower().strip()
        base = self.MOCK_DATA.get(key, {
            "temperature": 27, "feels_like": 30, "humidity": 60,
            "description": "Clear Sky", "wind_speed": 3.0,
        })
        return {
            "success": True,
            "city": city.title(),
            "country": "IN",
            "temperature": base["temperature"],
            "feels_like": base["feels_like"],
            "humidity": base["humidity"],
            "description": base["description"],
            "wind_speed": base["wind_speed"],
            "icon": "01d",
            "source": "Mock Data (add OPENWEATHER_API_KEY for live data)",
        }

    def _mock_forecast(self, city: str, days: int) -> Dict[str, Any]:
        weather = self._mock_weather(city)
        forecast = []
        for i in range(days):
            from datetime import timedelta
            day = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
            forecast.append({
                "date": day,
                "temp_min": weather["temperature"] - 3,
                "temp_max": weather["temperature"] + 2,
                "description": weather["description"],
                "humidity": weather["humidity"],
            })
        return {"success": True, "city": city.title(), "forecast": forecast}
