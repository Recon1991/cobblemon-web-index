import json
import os
import time
import sqlite3
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from bs4 import BeautifulSoup
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Load Pokémon names and dex numbers from JSON file
with open('pokemon_list_edit.json', 'r') as f:
    pokemon_list = json.load(f)

# Initialize the WebDriver (ensure the path to your WebDriver is correct)
driver = webdriver.Chrome(service=webdriver.chrome.service.Service('C:/Users/Recon/Desktop/chromedriver-win64/chromedriver.exe'))

# Open the website
driver.get('https://pokemonpalette.com/')

# Add an initial delay to allow the page to fully load before interacting
time.sleep(2)

# Function to check if an element exists
def element_exists(by, value):
    try:
        driver.find_element(by, value)
        return True
    except NoSuchElementException:
        return False

# Function to reset dropdown to the default form
def reset_dropdown():
    if element_exists(By.ID, 'optionsMenu'):
        try:
            form_dropdown = driver.find_element(By.ID, 'optionsMenu')
            if form_dropdown.is_displayed():
                options = form_dropdown.find_elements(By.TAG_NAME, 'option')
                if options:
                    options[0].click()  # Reset to the default form (first option)
                    time.sleep(1)
        except (NoSuchElementException, StaleElementReferenceException) as e:
            print(Fore.YELLOW + f"Failed to reset dropdown. Error: {str(e)}", flush=True)

# Function to extract data for a given Pokémon
def extract_pokemon_data(pokemon, shiny=False):
    pokemon_name = pokemon['name']
    dex_number = pokemon['dex_number']

    # Find the input field and enter the Pokémon name
    input_field = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="text"]'))
    )
    input_field.clear()
    input_field.send_keys(pokemon_name)
    time.sleep(2)  # Wait for the input to process

    # Extract base form color data
    base_data = extract_color_data(pokemon_name, dex_number, form_name='base')
    all_forms_data = [base_data]

    # Check if there are alternate forms available
    if element_exists(By.ID, 'optionsMenu'):
        try:
            form_dropdown = driver.find_element(By.ID, 'optionsMenu')
            if form_dropdown.is_displayed():
                options = form_dropdown.find_elements(By.TAG_NAME, 'option')
                for option in options:
                    form_value = option.get_attribute('value').strip()
                    if form_value.lower() != pokemon_name.lower():
                        # Select the form
                        option.click()
                        time.sleep(2)  # Wait for the form to load
                        print(Fore.CYAN + f"Extracting data for form: {option.text.strip()} of Pokémon: {pokemon_name}", flush=True)  # Debug: Form being processed
                        # Extract color data for the alternate form
                        form_name = option.text.strip() if option.text.strip().lower() != 'default form' else 'base'
                        form_data = extract_color_data(pokemon_name, dex_number, form_name)
                        all_forms_data.append(form_data)
                        print(Fore.GREEN + f"Appended form data for: {form_name}", flush=True)  # Debug: Form data appended
        except (NoSuchElementException, StaleElementReferenceException) as e:
            print(Fore.YELLOW + f"No dropdown or alternate forms found for: {pokemon_name}. Skipping forms. Error: {str(e)}", flush=True)

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
        'pokemon_name': pokemon_name,
        'form_name': form_name,
        'color_palette': colors
    }

# Extract data for each Pokémon and store in a list
all_pokemon_data = []
for pokemon in pokemon_list:
    forms_data = extract_pokemon_data(pokemon, shiny=True)
    all_pokemon_data.extend(forms_data)
    
    reset_dropdown()  # Reset dropdown to default form before moving to the next Pokémon

    time.sleep(2)  # Wait for input field to be ready for next entry

# Check if any data was extracted
if not all_pokemon_data:
    print(Fore.RED + "No data extracted! Check the HTML structure and extraction logic.", flush=True)

# Create a SQLite3 database and table
conn = sqlite3.connect('pokemon_palettes.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS pokemon_colors (
        shiny BOOLEAN,
        dex_number TEXT,
        pokemon_name TEXT,
        form_name TEXT,
        color1 TEXT,
        color2 TEXT,
        color3 TEXT,
        color4 TEXT,
        color5 TEXT,
        color6 TEXT,
        color7 TEXT,
        color8 TEXT,
        color9 TEXT,
        PRIMARY KEY (dex_number, pokemon_name, form_name, shiny)
    )
''')

# Insert the data into the SQLite3 database
for pokemon in all_pokemon_data:
    shiny = False
    colors = pokemon['color_palette']
    colors += [None] * (9 - len(colors))  # Ensure there are always 9 color slots
    print(Fore.MAGENTA + f"Inserting into DB: {pokemon['pokemon_name']} (Dex: {pokemon['dex_number']}), Form: {pokemon['form_name']}", flush=True)  # Debug: Data being inserted
    cursor.execute('''
        INSERT OR REPLACE INTO pokemon_colors (dex_number, pokemon_name, form_name, shiny, color1, color2, color3, color4, color5, color6, color7, color8, color9)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (pokemon['dex_number'], pokemon['pokemon_name'], pokemon['form_name'], shiny, *colors))

# Commit changes and close the connection
conn.commit()
conn.close()

# Verify database contents
conn = sqlite3.connect('pokemon_palettes.db')
cursor = conn.cursor()

cursor.execute('SELECT * FROM pokemon_colors')
rows = cursor.fetchall()

if not rows:
    print(Fore.RED + "The database is empty.", flush=True)

conn.close()

# Close the WebDriver
driver.quit()
