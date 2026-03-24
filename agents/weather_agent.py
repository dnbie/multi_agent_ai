"""
Weather Agent - Fetch weather information and generate smart advice using LLM
Reuses: WeatherAPI (tools/weather_api.py), LLMTool (tools/llm_tool.py)
"""

import re
from typing import Dict, List
from .base_agent import BaseAgent, AgentResult


class WeatherAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            name="Weather Agent",
            description="Get current weather and AI-powered situational advice"
        )
        from tools.weather_api import WeatherAPI
        self.weather_api = WeatherAPI()

    def get_capabilities(self) -> List[str]:
        return [
            "Current weather for any city",
            "3-day weather forecast",
            "AI advice (umbrella, clothing, travel tips)",
            "Temperature, humidity, wind speed",
        ]

    def execute(self, task: str, **kwargs) -> AgentResult:
        self._start_execution(task)
        try:
            city = kwargs.get("city") or self._extract_city(task)
            if not city:
                result = self._create_result(
                    False, "Please specify a city. Example: 'Weather in Chennai today'",
                    error="City not found in task"
                )
                self._end_execution(result)
                return result

            result = self._build_result(city, task)
        except Exception as e:
            result = self._create_result(False, f"Weather agent error: {str(e)}", error=str(e))

        self._end_execution(result)
        return result

    # ── helpers ───────────────────────────────────────────────────────────────

    def _build_result(self, city: str, task: str) -> AgentResult:
        weather = self.weather_api.get_current_weather(city)
        forecast = self.weather_api.get_forecast(city, days=3)

        if not weather.get("success"):
            return self._create_result(False, f"Could not get weather for {city}",
                                       error=weather.get("error", "Unknown error"))

        # LLM advice
        advice = self._get_advice(weather, task)

        display = (
            f"Weather in {weather['city']}: {weather['description']}, "
            f"{weather['temperature']}°C (feels like {weather['feels_like']}°C), "
            f"Humidity {weather['humidity']}%, Wind {weather['wind_speed']} m/s"
        )

        return self._create_result(True, display, data={
            "city": weather["city"],
            "current": weather,
            "forecast": forecast.get("forecast", []),
            "advice": advice,
            "source": weather.get("source", ""),
        })

    def _get_advice(self, weather: Dict, original_task: str) -> str:
        try:
            llm = self.get_llm()
            prompt = (
                f"Weather in {weather['city']}: {weather['description']}, "
                f"{weather['temperature']}°C, humidity {weather['humidity']}%, "
                f"wind {weather['wind_speed']} m/s.\n"
                f"User asked: \"{original_task}\"\n\n"
                "Give 2-3 practical tips (umbrella, clothing, outdoor activity, travel). "
                "Be concise and helpful."
            )
            return llm.generate_text(prompt, temperature=0.5)
        except Exception:
            temp = weather["temperature"]
            desc = weather["description"].lower()
            if "rain" in desc or "thunder" in desc:
                return "Carry an umbrella. Avoid outdoor activities."
            if temp > 35:
                return "Stay hydrated. Wear light clothing and avoid direct sun."
            if temp < 15:
                return "Wear warm layers. Good day to carry a jacket."
            return "Weather looks pleasant. Enjoy your day!"

    def _extract_city(self, text: str) -> str:
        patterns = [
            r'weather\s+(?:in|at|for)\s+([a-z\s]+?)(?:\s+today|\s+tomorrow|\s+this|\?|$)',
            r'(?:in|at|for)\s+([a-z\s]+?)\s+weather',
            r'weather\s+([a-z\s]+)',
        ]
        lower = text.lower()
        for pat in patterns:
            m = re.search(pat, lower)
            if m:
                city = m.group(1).strip().rstrip("?.,")
                if len(city) > 1:
                    return city
        return ""
