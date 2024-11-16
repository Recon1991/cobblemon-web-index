import requests
import json

# Fetch Pokémon data from PokeAPI
response = requests.get('https://pokeapi.co/api/v2/pokemon?limit=10000')
if response.status_code == 200:
    data = response.json()
    pokemon_list = []

    # Fetch dex number for each Pokémon
    for entry in data['results']:
        pokemon_name = entry['name']
        pokemon_details_response = requests.get(entry['url'])
        
        if pokemon_details_response.status_code == 200:
            pokemon_details = pokemon_details_response.json()
            dex_number = pokemon_details['id']
            
            # Add Pokémon name and dex number to list
            pokemon_list.append({
                "name": pokemon_name,
                "dex_number": dex_number
            })

    # Save Pokémon names and dex numbers to a JSON file
    with open('pokemon_list.json', 'w') as f:
        json.dump(pokemon_list, f, indent=4)

    print("Pokémon list with dex numbers saved successfully!")
else:
    print("Failed to fetch data from PokeAPI.")
