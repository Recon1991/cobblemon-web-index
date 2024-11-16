import json
import os
import time
import sqlite3
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Load Pokémon names and dex numbers from JSON file
with open('pokemon_list_testform.json', 'r') as f:
    pokemon_list = json.load(f)

# Initialize the WebDriver (ensure the path to your WebDriver is correct)
driver = webdriver.Chrome(service=webdriver.chrome.service.Service('C:/Users/Recon/Desktop/chromedriver-win64/chromedriver.exe'))

# Open the website
driver.get('https://pokemonpalette.com/')

# Add an initial delay to allow the page to fully load before interacting
time.sleep(5)

# Function to extract data for a given Pokémon
def extract_pokemon_data(pokemon):
    pokemon_name = pokemon['name']
    dex_number = pokemon['dex_number']

    # Find the input field and enter the Pokémon name
    input_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="text"]'))
    )
    input_field.clear()
    input_field.send_keys(pokemon_name)

    # Reset the form dropdown to default (first option)
    try:
        form_dropdown = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'optionsMenu'))
        )
        if form_dropdown:
            options = form_dropdown.find_elements(By.TAG_NAME, 'option')
            if options:
                options[0].click()  # Reset to the default form (first option)
    except Exception as e:
        print(f"Could not reset form dropdown for: {pokemon_name}. Error: {str(e)}", flush=True)

    # Wait for the results to load
    time.sleep(3)  # Increase sleep time to ensure results are loaded

    # Extract base form color data
    base_data = extract_color_data(pokemon_name, dex_number)
    all_forms_data = [base_data]

    # Check if there are alternate forms available
    try:
        form_dropdown = driver.find_element(By.ID, 'optionsMenu')
        if form_dropdown:
            options = form_dropdown.find_elements(By.TAG_NAME, 'option')
            for option in options:
                form_value = option.get_attribute('value').strip()
                if form_value.lower() != pokemon_name.lower():
                    # Select the form
                    option.click()
                    time.sleep(2)  # Wait for the form to load

                    # Extract color data for the alternate form
                    form_name = option.text.strip()
                    form_data = extract_color_data(pokemon_name, dex_number, form_name)
                    all_forms_data.append(form_data)
    except Exception as e:
        print(f"No alternate forms found for: {pokemon_name}", flush=True)

    return all_forms_data

# Helper function to extract color data for a given form
def extract_color_data(pokemon_name, dex_number, form_name='base'):
    # Extract CSS variables for colors using JavaScript
    script = """
    const styles = getComputedStyle(document.documentElement);
    return {
        color2: styles.getPropertyValue('--color2').trim(),
        color3: styles.getPropertyValue('--color3').trim(),
        color4: styles.getPropertyValue('--color4').trim(),
        color5: styles.getPropertyValue('--color5').trim(),
        color6: styles.getPropertyValue('--color6').trim(),
        color7: styles.getPropertyValue('--color7').trim(),
        color8: styles.getPropertyValue('--color8').trim(),
        color9: styles.getPropertyValue('--color9').trim(),
        color10: styles.getPropertyValue('--color10').trim()
    };
    """
    color_data = driver.execute_script(script)
    colors = [color_data.get(f'color{i}', None) for i in range(2, 11)]

    return {
        'dex_number': dex_number,
        'pokemon_name': f"{pokemon_name} ({form_name})",
        'color_palette': colors
    }

# Extract data for each Pokémon and store in a list
all_pokemon_data = []
for pokemon in pokemon_list:
    forms_data = extract_pokemon_data(pokemon)
    for data in forms_data:
        if data:
            print(f"Extracted data: {data}", flush=True)  # Debug: Print the extracted data
            all_pokemon_data.append(data)
        else:
            print(f"No data found for: {pokemon['name']}", flush=True)  # Debug: If no data is found
    time.sleep(1)  # To prevent overwhelming the server

# Check if any data was extracted
if not all_pokemon_data:
    print("No data extracted! Check the HTML structure and extraction logic.", flush=True)

# Create a SQLite3 database and table
conn = sqlite3.connect('pokemon_palettes.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS pokemon_colors (
        dex_number TEXT,
        pokemon_name TEXT,
        color1 TEXT,
        color2 TEXT,
        color3 TEXT,
        color4 TEXT,
        color5 TEXT,
        color6 TEXT,
        color7 TEXT,
        color8 TEXT,
        color9 TEXT,
        PRIMARY KEY (dex_number, pokemon_name)
    )
''')

# Insert the data into the SQLite3 database
for pokemon in all_pokemon_data:
    colors = pokemon['color_palette']
    colors += [None] * (9 - len(colors))  # Ensure there are always 9 color slots
    cursor.execute('''
        INSERT OR REPLACE INTO pokemon_colors (dex_number, pokemon_name, color1, color2, color3, color4, color5, color6, color7, color8, color9)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (pokemon['dex_number'], pokemon['pokemon_name'], *colors))
    print(f"Inserted into DB: {pokemon['pokemon_name']} (Dex: {pokemon['dex_number']})", flush=True)  # Debug: Log insertion into DB

# Commit changes and close the connection
conn.commit()
conn.close()

# Verify database contents
conn = sqlite3.connect('pokemon_palettes.db')
cursor = conn.cursor()

cursor.execute('SELECT * FROM pokemon_colors')
rows = cursor.fetchall()

if rows:
    for row in rows:
        print(row, flush=True)
else:
    print("The database is empty.", flush=True)

conn.close()

# Close the WebDriver
driver.quit()
