from selenium import webdriver
import time
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.chrome.service import Service
import os
import requests
import datetime
import config

# ---------------------------------------------
# Set your local file path here
file_path = '<INSERT_YOUR_LOCAL_PATH_HERE>/'  # ← Example: 'C:/Users/YourName/Desktop/data/'

# Check if the path has been updated
if '<INSERT_YOUR_LOCAL_PATH_HERE>' in file_path:
    raise ValueError("Please update 'file_path' with the path to your local directory.")
# ---------------------------------------------

# Check if the file city_names.csv exists. If yes, read it into a DataFrame
if os.path.exists(file_path + 'city_names.csv'):
    cities_df = pd.read_csv(file_path + 'city_names.csv')
else:
    # Create a service for the Chrome WebDriver
    webdriver_service = Service("./chromedriver")
    # Create a Chrome browser instance controlled by chromedriver
    driver = webdriver.Chrome(service=webdriver_service)
    # Send a GET request to the target URL
    driver.get('https://worldpopulationreview.com/world-cities')
    # Maximize the browser window
    driver.maximize_window()
    # Wait for 2 seconds to allow the page to load properly
    time.sleep(2)

    # Get the full HTML content of the page and parse it using BeautifulSoup with the lxml parser
    cities = BeautifulSoup(driver.page_source, "lxml")

    # Extract city names from anchor tags
    city_names = []
    for i in range(52, 452):
        if i % 2 == 0:
            city_names.append(cities.findAll('a')[i].getText())

    # Extract city populations from table data cells
    city_populations = []
    for i in range(1000):
        if i % 5 == 0:
            city_populations.append(cities.findAll('td')[i + 2].getText())

    # Create a DataFrame with the extracted city names and populations
    city_names_pop = pd.DataFrame(data={"city_names": city_names, "population": city_populations})

    # Save the DataFrame to a CSV file
    city_names_pop.to_csv(file_path + 'city_names.csv', index=False)

    # Assign the DataFrame to cities_df
    cities_df = city_names_pop

# Store city names and populations as lists
city_names = cities_df['city_names'].values.tolist()
city_populations = cities_df['population'].values.tolist()

# Function to get current weather data from OpenWeatherMap API
def getCurrentWeather(params):
    weather = 'http://api.openweathermap.org/data/2.5/weather'
    params['APPID'] = config.appid
    params['units'] = 'metric'
    return requests.get(weather, params)

# Function to correct some city names for better API compatibility
def get_correct_name(city_name):
    correct_name = city_name
    if city_name == 'St Petersburg':
        correct_name = 'St. Petersburg,RU'
    elif city_name == 'Rome':
        correct_name = 'Rome,IT'
    elif city_name == 'Melbourne':
        correct_name = 'Melbourne,AU'
    return correct_name

# Get today's date
d = datetime.date.today()

# Print a message to indicate weather data is being updated
print('Updating Weather Conditions...')

params = {}
world_temperatures = []

# Loop through the first 200 cities to fetch weather data
for i in range(200):
    params['q'] = get_correct_name(city_names[i])
    response = getCurrentWeather(params)

    # Skip the city if the API call was unsuccessful
    if response.status_code != 200:
        continue

    # Parse the JSON response
    city_information = response.json()
    country = city_information['sys']['country']
    latitude = city_information['coord']['lat']
    longitude = city_information['coord']['lon']
    weather_condition = city_information['weather'][0]['main']
    weather_det = city_information['weather'][0]['description']
    feels_like = city_information['main']['feels_like']
    temp = city_information['main']['temp']
    max_temp = city_information['main']['temp_max']
    min_temp = city_information['main']['temp_min']
    wind_speed = city_information['wind']['speed']

    # Create a dictionary with all relevant weather data
    city_data = {
        'City': city_names[i],
        'Country': country,
        'Date': d.strftime('%d-%m-%Y'),
        'Latitude': latitude,
        'Longitude': longitude,
        'Population': city_populations[i],
        'Weather': weather_condition,
        'Main_Weather': weather_det,
        'Feels_like': feels_like,
        'temp': temp,
        'max_temp': max_temp,
        'min_temp': min_temp,
        'Wind_Speed': wind_speed
    }

    world_temperatures.append(city_data)

# Create a DataFrame from the list of city weather data
world_temps_df = pd.DataFrame(world_temperatures, columns=city_data.keys())

# Save the DataFrame to a CSV file
world_temps_df.to_csv(file_path + 'weather.csv', index=False)

print('Weather Update Complete')
