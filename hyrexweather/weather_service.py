import requests
from config import NWS_BASE_URL, SF_ZONE_ID

def get_sf_weather():
    """Get San Francisco weather forecast from NWS API"""
    url = f"{NWS_BASE_URL}/zones/forecast/{SF_ZONE_ID}/forecast"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for HTTP errors
        data = response.json()
        return data['properties']['periods']
    #data has periods represented as "today, tonight, tomorrow. each with its weather data"
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather: {e}")
        return None
    
def todays_weather() -> str:
    forecast_periods = get_sf_weather()
    
    if not forecast_periods:
        return "Unable to retrieve weather data for San Francisco"
    
    #get the first two periods (typically "Rest of Today" and "Tonight")
    today = forecast_periods[0]
    tonight = forecast_periods[1] if len(forecast_periods) > 1 else None
    
    #create a formatted message
    message = f"{today['name']}: {today['detailedForecast']} "

    if tonight:
        message += f"{tonight['name']}: {tonight['detailedForecast']}"
    
    return message

#note: name more specifically so readers can understand at glance