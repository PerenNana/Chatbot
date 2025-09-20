from pydantic import BaseModel, Field
from langchain_core.tools import tool
import requests

class WeatherInput(BaseModel):
    city: str = Field(..., description="Name of the city for the weather forecast")

class WeatherOutput(BaseModel):
    city: str = Field(..., description="City for which the weather was retrieved")
    temperature: float = Field(..., description="Current temperature in Celsius")
    wind_speed: float = Field(..., description="Current wind speed in km/h")
    english_answer: str = Field(..., description="A human-readable summary of the weather")
    german_answer: str = Field(..., description="Eine menschenlesbare Zusammenfassung des Wetters")

@tool(args_schema=WeatherInput)
def get_weather(city: str) -> WeatherOutput:
    """
    Predicts the weather in a given city.

    Usage: weather(city: str)

    Returns:
        WeatherOutput object if successful, otherwise an error string describing the issue.
    """
    try:
        # Use a geocoding API to get latitude and longitude from the city name
        geocoding_url = f"https://nominatim.openstreetmap.org/search?city={city}&format=json"
        headers = {"User-Agent": "WeatherTool/1.0 (paul.nana-nana@eoniq.ai)"}
        response = requests.get(geocoding_url, headers=headers)
        response.raise_for_status()
        data = response.json()

        if not data:
            return f"Error: Could not find coordinates for city '{city}'"

        latitude = data[0]["lat"]
        longitude = data[0]["lon"]

        # Fetch weather data using the coordinates
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
        weather_response = requests.get(weather_url)
        weather_response.raise_for_status()
        weather_data = weather_response.json()

        if "current_weather" not in weather_data:
            return f"Error: Could not fetch weather data for city '{city}'"

        current_weather = weather_data["current_weather"]
        temperature = current_weather["temperature"]
        wind_speed = current_weather.get("windspeed")
        if wind_speed is None:
            wind_speed = float('nan')

        return WeatherOutput(city=city, 
                             temperature=temperature, 
                             wind_speed=wind_speed,
                             )

    except Exception as e:
        return f"Error: {e}"


