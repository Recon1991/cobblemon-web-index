import json
import sqlite3

def initialize_database(db_name="pokemon_data.db"):
    """
    Initialize the SQLite database with the required tables.
    """
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    # Create tables for core Pokémon data, forms, evolutions, moves, and behaviors
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pokemon (
            dex_number INTEGER PRIMARY KEY,
            pokemon_name TEXT,
            primary_type TEXT,
            secondary_type TEXT,
            egg_groups TEXT,
            catch_rate INTEGER,
            base_experience_yield INTEGER,
            base_friendship INTEGER,
            generation TEXT,
            labels TEXT,
            primary_ability TEXT,
            hidden_ability TEXT,
            secondary_abilities TEXT,
            movement_type TEXT,
            rest_type TEXT,
            height REAL,
            weight REAL,
            base_scale REAL,
            hitbox_width REAL,
            hitbox_height REAL,
            drops TEXT,
            base_stats TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS forms (
            form_id INTEGER PRIMARY KEY AUTOINCREMENT,
            dex_number INTEGER,
            form_name TEXT,
            base_stats TEXT,
            height REAL,
            weight REAL,
            abilities TEXT,
            moves TEXT,
            evolutions TEXT,
            FOREIGN KEY (dex_number) REFERENCES pokemon (dex_number)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS evolutions (
            evolution_id INTEGER PRIMARY KEY AUTOINCREMENT,
            dex_number INTEGER,
            evolves_to TEXT,
            evolution_level INTEGER,
            conditions TEXT,
            FOREIGN KEY (dex_number) REFERENCES pokemon (dex_number)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS moves (
            move_id INTEGER PRIMARY KEY AUTOINCREMENT,
            dex_number INTEGER,
            category TEXT,
            move_name TEXT,
            FOREIGN KEY (dex_number) REFERENCES pokemon (dex_number)
        )
    ''')

    connection.commit()
    connection.close()

def insert_pokemon_data(extracted_data, db_name="pokemon_data.db"):
    """
    Insert extracted Pokémon data into the SQLite database.
    """
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()

    # Insert core Pokémon data
    cursor.execute('''
        INSERT OR REPLACE INTO pokemon (
            dex_number, pokemon_name, primary_type, secondary_type, egg_groups,
            catch_rate, base_experience_yield, base_friendship, generation, labels,
            primary_ability, hidden_ability, secondary_abilities, movement_type, rest_type,
            height, weight, base_scale, hitbox_width, hitbox_height, drops, base_stats
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        extracted_data["dex_number"],
        extracted_data["pokemon_name"],
        extracted_data["primary_type"],
        extracted_data["secondary_type"],
        extracted_data["egg_groups"],
        extracted_data["catch_rate"],
        extracted_data["base_experience_yield"],
        extracted_data["base_friendship"],
        extracted_data["generation"],
        extracted_data["labels"],
        extracted_data["primary_ability"],
        extracted_data["hidden_ability"],
        extracted_data["secondary_abilities"],
        extracted_data["movement_type"],
        extracted_data["rest_type"],
        extracted_data["height"],
        extracted_data["weight"],
        extracted_data["base_scale"],
        extracted_data["hitbox_width"],
        extracted_data["hitbox_height"],
        extracted_data["drops"],
        json.dumps(extracted_data["base_stats"])
    ))

    # Insert forms data
    for form in extracted_data["forms"]:
        cursor.execute('''
            INSERT INTO forms (
                dex_number, form_name, base_stats, height, weight, abilities, moves, evolutions
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            extracted_data["dex_number"],
            form["form_name"],
            json.dumps(form["base_stats"]),
            form["height"],
            form["weight"],
            json.dumps(form["abilities"]),
            json.dumps(form["moves"]),
            json.dumps(form["evolutions"])
        ))

    # Insert evolutions data
    for evolution in extracted_data["evolutions"]:
        cursor.execute('''
            INSERT INTO evolutions (
                dex_number, evolves_to, evolution_level, conditions
            ) VALUES (?, ?, ?, ?)
        ''', (
            extracted_data["dex_number"],
            evolution["evolves_to"],
            evolution["evolution_level"],
            json.dumps(evolution["conditions"])
        ))

    # Insert moves data
    for category, moves in extracted_data["moves"].items():
        for move in moves:
            cursor.execute('''
                INSERT INTO moves (
                    dex_number, category, move_name
                ) VALUES (?, ?, ?)
            ''', (
                extracted_data["dex_number"],
                category,
                move
            ))

    connection.commit()
    connection.close()

# Example usage with the provided JSON data
with open('cyndaquil.json', 'r') as f:
    cyndaquil_data = json.load(f)
    extracted_data = extract_species_info(cyndaquil_data)

# Initialize the database and insert data
initialize_database()
insert_pokemon_data(extracted_data)
