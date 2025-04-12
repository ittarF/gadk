import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
import requests
from typing import Dict, Any, List, Optional
from google.adk.tools import google_search

def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city for which to retrieve the weather report.

    Returns:
        dict: status and result or error msg.
    """
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": (
                "The weather in New York is sunny with a temperature of 25 degrees"
                " Celsius (41 degrees Fahrenheit)."
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available.",
        }

def real_weather(city: str) -> dict:
    """Get real weather data for a location using Open-Meteo API"""
    try:
        # First, geocode the city to get coordinates
        geocode_url = "https://geocoding-api.open-meteo.com/v1/search"
        geocode_params = {
            "name": city,
            "count": 1,
            "language": "en",
            "format": "json"
        }
            
        geocode_response = requests.get(geocode_url, params=geocode_params)
        geocode_response.raise_for_status()
        geocode_data = geocode_response.json()
        
        if not geocode_data.get("results"):
            return {"error": f"Could not find location: {city}"}
        
        # Get the first result
        location = geocode_data["results"][0]
        lat = location["latitude"]
        lon = location["longitude"]
        location_name = location["name"]
        country = location.get("country", "Unknown")
        
        # Call Open-Meteo API (free, no API key required)
        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,wind_speed_10m,wind_direction_10m,weather_code",
            "hourly": "temperature_2m,relative_humidity_2m",
            "timezone": "auto"
        }
        
        weather_response = requests.get(weather_url, params=weather_params)
        weather_response.raise_for_status()
        weather_data = weather_response.json()
         
        # Map weather codes to conditions
        weather_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            56: "Light freezing drizzle",
            57: "Dense freezing drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            66: "Light freezing rain",
            67: "Heavy freezing rain",
            71: "Slight snow fall",
            73: "Moderate snow fall",
            75: "Heavy snow fall",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }
        
        current = weather_data["current"]
        weather_code = current.get("weather_code", 0)
        weather_description = weather_codes.get(weather_code, "Unknown")
        
        # Extract relevant weather information
        return {
            "status": "success",
            "report": {
                "city": location_name,
                "country": country,
                "coordinates": {
                    "latitude": lat,
                    "longitude": lon
                },
                "temperature": {
                    "current": current["temperature_2m"],
                    "apparent": current["apparent_temperature"],
                    "unit": weather_data["current_units"]["temperature_2m"]
                },
                "humidity": {
                    "value": current["relative_humidity_2m"],
                    "unit": weather_data["current_units"]["relative_humidity_2m"]
                },
                "precipitation": {
                    "value": current["precipitation"],
                    "unit": weather_data["current_units"]["precipitation"]
                },
                "wind": {
                    "speed": current["wind_speed_10m"],
                    "speed_unit": weather_data["current_units"]["wind_speed_10m"],
                    "direction": current["wind_direction_10m"],
                    "direction_unit": weather_data["current_units"]["wind_direction_10m"]
                },
                "weather": {
                    "code": weather_code,
                    "description": weather_description
                },
                "timestamp": current["time"]
                }
            }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available. | {e}",
        }
    except (KeyError, IndexError, ValueError) as e:
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available. | {e}",
        }


def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city.

    Args:
        city (str): The name of the city for which to retrieve the current time.

    Returns:
        dict: status and result or error msg.
    """

    if city.lower() == "new york":
        tz_identifier = "America/New_York"
    else:
        return {
            "status": "error",
            "error_message": (
                f"Sorry, I don't have timezone information for {city}."
            ),
        }

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    report = (
        f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
    )
    return {"status": "success", "report": report}


root_agent = Agent(
    name="weather_time_agent",
    model="gemini-2.0-flash-exp",
    description=(
        "Agent to answer questions about the time and weather in a city."
    ),
    instruction=(
        "I can answer your questions about the time and weather in a city."
    ),
    tools=[google_search],
)