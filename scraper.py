import json
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Load Pokémon names from JSON file
with open('pokemon_list.json', 'r') as f:
    pokemon_list = json.load(f)

# Initialize the WebDriver (ensure the path to your WebDriver is correct)
driver = webdriver.Chrome(service=webdriver.chrome.service.Service('C:/Users/Recon/Desktop/chromedriver-win64/chromedriver.exe'))

# Open the website
driver.get('https://pokemonpalette.com/')

# Function to extract data for a given Pokémon
def extract_pokemon_data(pokemon_name):
    # Find the input field and enter the Pokémon name
    input_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="text"]'))
    )
    input_field.clear()
    input_field.send_keys(pokemon_name)

    # Wait for the results to load
    time.sleep(2)  # Adjust sleep time if necessary

    # Parse the page content
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Extract the color palette
    color_elements = soup.select('.color-box')
    colors = [elem.get_text(strip=True) for elem in color_elements]

    # Extract the Pokémon name and dex number
    name_element = soup.select_one('.pokemon-name')
    dex_number_element = soup.select_one('.pokemon-number')

    if name_element and dex_number_element:
        name = name_element.get_text(strip=True)
        dex_number = dex_number_element.get_text(strip=True).replace('#', '')
        return {
            'dex_number': dex_number,
            'pokemon_name': name,
            'color_palette': colors
        }
    else:
        return None

# Extract data for each Pokémon and store in a list
all_pokemon_data = []
for pokemon in pokemon_list:
    data = extract_pokemon_data(pokemon)
    if data:
        all_pokemon_data.append(data)
    time.sleep(1)  # To prevent overwhelming the server

# Save the data to a JSON file
with open('pokemon_palettes.json', 'w') as f:
    json.dump(all_pokemon_data, f, indent=4)

# Close the WebDriver
driver.quit()