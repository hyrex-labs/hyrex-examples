import time
from datetime import datetime
from config import CHECK_INTERVAL_HOURS
from weather_service import get_sf_weather, todays_weather
from slack_service import send_weather_notification
from hyrex import HyrexRegistry

hy = HyrexRegistry()


@hy.task(cron="0 16 * * 1-5")
def check_and_notify():
    print('Checking San Francisco weather...')
    # retrieve forecast data and validate it
    forecast_periods = get_sf_weather()
    if not forecast_periods:
        print("Failed to retrieve weather data")
        raise Exception("Failed to retrieve weather data")
    # dont swallow errors!!
    # get formatted weather message
    weather_message = todays_weather()
    print(weather_message)

    # convert the weather message into an alert format that slack_service can handle
    forecast_alert = {
        'period': 'Weather Forecast',
        'forecast': weather_message
    }

    # add the forecast as the bulliten
    weather_bulliten = [forecast_alert]

    # Send to Slack
    send_weather_notification(weather_bulliten)
    # print(weather_bulliten)


# 1. get today's weather
# 1b. check for weather events/alerts (rain, wind, etc)
# 2. post the forecast to slack

@hy.task
def hello_performance():
    print("hello performance!")

@hy.task
def hello_performance_times_10():
    for _ in range(10):
        hello_performance.send()

@hy.task
def hello_performance_times_n(n: int):
    for _ in range(n):
        hello_performance.send()

if __name__ == "__main__":
    check_and_notify()
