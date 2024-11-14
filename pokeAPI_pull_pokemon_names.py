import requests
import json

# Fetch Pokémon data from PokeAPI
response = requests.get('https://pokeapi.co/api/v2/pokemon?limit=10000')
if response.status_code == 200:
    data = response.json()
    pokemon_list = [entry['name'] for entry in data['results']]

    # Save Pokémon names to a JSON file
    with open('pokemon_list.json', 'w') as f:
        json.dump(pokemon_list, f, indent=4)

    print("Pokémon list saved successfully!")
else:
    print("Failed to fetch data from PokeAPI.")