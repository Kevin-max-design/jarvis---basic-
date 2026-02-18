"""
Weather Tool — Gets REAL weather data (free, no API key).
Uses wttr.in — a free weather service.
"""
import requests
import json


def get_weather(location=""):
    """Get real weather data for a location. If no location, uses IP-based location."""
    try:
        if not location:
            location = ""  # wttr.in auto-detects location from IP

        url = f"https://wttr.in/{location}?format=j1"
        resp = requests.get(url, timeout=10, headers={"User-Agent": "JARVIS-AI/1.0"})
        resp.raise_for_status()
        data = resp.json()

        current = data.get("current_condition", [{}])[0]
        area = data.get("nearest_area", [{}])[0]

        city = area.get("areaName", [{"value": "Unknown"}])[0]["value"]
        country = area.get("country", [{"value": ""}])[0]["value"]
        temp_c = current.get("temp_C", "N/A")
        temp_f = current.get("temp_F", "N/A")
        feels_like_c = current.get("FeelsLikeC", "N/A")
        humidity = current.get("humidity", "N/A")
        description = current.get("weatherDesc", [{"value": "N/A"}])[0]["value"]
        wind_speed = current.get("windspeedKmph", "N/A")
        wind_dir = current.get("winddir16Point", "N/A")

        # Get today's forecast
        today = data.get("weather", [{}])[0]
        max_temp_c = today.get("maxtempC", "N/A")
        min_temp_c = today.get("mintempC", "N/A")
        sunrise = today.get("astronomy", [{}])[0].get("sunrise", "N/A") if today.get("astronomy") else "N/A"
        sunset = today.get("astronomy", [{}])[0].get("sunset", "N/A") if today.get("astronomy") else "N/A"

        return json.dumps({
            "location": f"{city}, {country}",
            "temperature": f"{temp_c}°C ({temp_f}°F)",
            "feels_like": f"{feels_like_c}°C",
            "condition": description,
            "humidity": f"{humidity}%",
            "wind": f"{wind_speed} km/h {wind_dir}",
            "high": f"{max_temp_c}°C",
            "low": f"{min_temp_c}°C",
            "sunrise": sunrise,
            "sunset": sunset,
        })

    except Exception as e:
        return json.dumps({"error": str(e)})


def get_news(topic=""):
    """Get latest news headlines using DuckDuckGo."""
    try:
        from duckduckgo_search import DDGS
        ddgs = DDGS()
        query = f"{topic} latest news" if topic else "latest news today"
        results = list(ddgs.news(query, max_results=5))

        if not results:
            # Fallback to text search
            results = list(ddgs.text(f"{query}", max_results=5))

        headlines = []
        for r in results:
            headlines.append({
                "title": r.get("title", ""),
                "body": r.get("body", r.get("snippet", "")),
                "source": r.get("source", r.get("href", "")),
            })
        return json.dumps(headlines)
    except Exception as e:
        return json.dumps({"error": str(e)})
