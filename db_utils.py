import sqlite3
import json
import logging
from contextlib import closing

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def initialize_database(db_name="pokemon_data.db"):
    """
    Initialize the SQLite database with the required tables.
    """
    with closing(sqlite3.connect(db_name)) as connection:
        cursor = connection.cursor()

        # Create tables for core Pokémon data, forms, evolutions, moves, and behaviors
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pokemon (
                dex_number INTEGER,
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
                base_stats TEXT,
                raw_data TEXT,
                PRIMARY KEY (dex_number, pokemon_name)  -- Composite primary key to differentiate forms
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS forms (
                form_id INTEGER PRIMARY KEY AUTOINCREMENT,
                dex_number INTEGER,
                pokemon_name TEXT,
                form_name TEXT,
                primary_type TEXT,
                secondary_type TEXT,
                egg_groups TEXT,
                catch_rate INTEGER,
                base_experience_yield INTEGER,
                base_friendship INTEGER,
                labels TEXT,
                primary_ability TEXT,
                hidden_ability TEXT,
                secondary_abilities TEXT,
                height REAL,
                weight REAL,
                base_stats TEXT,
                raw_data TEXT,
                FOREIGN KEY (dex_number) REFERENCES pokemon (dex_number)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evolutions (
                evolution_id INTEGER PRIMARY KEY AUTOINCREMENT,
                evolves_from TEXT,
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
        logging.info("Database initialized successfully.")

def insert_pokemon_data(extracted_data, connection):
    """
    Insert extracted Pokémon data into the SQLite database.
    """
    with closing(connection.cursor()) as cursor:
        try:
            # Begin a transaction for bulk insertion
            # Ensure abilities are handled correctly if they are lists
            primary_ability = extracted_data.get("primary_ability", "")
            hidden_ability = extracted_data.get("hidden_ability", "")
            secondary_abilities = extracted_data.get("secondary_abilities", "")
          
            # Extract labels from the data
            labels = extracted_data.get("labels", [])

            # Ensure labels is always treated as a list of strings
            if isinstance(labels, str):
                labels = labels.split(', ')
            elif isinstance(labels, list):
                labels = [str(label) for label in labels]
            # Ensure labels is always treated as a list of strings
            if isinstance(labels, str):
                labels = [labels]
            elif isinstance(labels, list):
                labels = [str(label) for label in labels]
            # Clone the original labels for the database insertion
            all_labels = labels.copy()
            # Convert all_labels to a comma-separated string for database insertion
            all_labels_str = ', '.join(all_labels)
            # Filter labels to extract only the generation information
            generation_label = next((label for label in labels if isinstance(label, str) and label.lower().startswith("gen")), None)
            # Determine the generation value
            generation_edit = generation_label if generation_label else "Unknown"
            # Filter out the generation label to keep only non-generation labels
            non_generation_labels = [label for label in labels if isinstance(label, str) and not label.lower().startswith("gen")]
            movement_type = extracted_data.get("behaviour", {}).get("moving", "")
            rest_type = extracted_data.get("behaviour", {}).get("resting", "")

            # Insert core Pokémon data
            cursor.execute('''
                INSERT OR REPLACE INTO pokemon (
                    dex_number, pokemon_name, primary_type, secondary_type, egg_groups,
                    catch_rate, base_experience_yield, base_friendship, generation, labels,
                    primary_ability, hidden_ability, secondary_abilities, movement_type, rest_type,
                    height, weight, base_scale, hitbox_width, hitbox_height, drops, base_stats, raw_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                int(extracted_data["dex_number"]),
                extracted_data["pokemon_name"],
                extracted_data["primary_type"],
                extracted_data["secondary_type"],
                extracted_data["egg_groups"],
                int(extracted_data.get("catch_rate", 0)),
                int(extracted_data.get("base_experience_yield", 0)),
                int(extracted_data.get("base_friendship", 0)),
                generation_edit,
                all_labels_str,
                primary_ability,
                hidden_ability,
                secondary_abilities,
                movement_type,
                rest_type,
                float(extracted_data.get("height", 0.0)),
                float(extracted_data.get("weight", 0.0)),
                float(extracted_data.get("base_scale", 1.0)),
                float(extracted_data.get("hitbox_width", 0.0)),
                float(extracted_data.get("hitbox_height", 0.0)),
                json.dumps(extracted_data.get("drops", []) if isinstance(extracted_data.get("drops"), list) else [extracted_data.get("drops")]),
                json.dumps(extracted_data["base_stats"]),
                json.dumps(extracted_data.get("raw_data", {}))
            ))

            # Insert forms data (e.g., Mega, Gmax)
            form_inserts = []
            for form in extracted_data.get("forms", []):
                form_name = form.get("name", form.get("form_name", "Unknown Form"))

                form_abilities = form.get("abilities", [])
                form_primary_ability = ""
                form_hidden_ability = ""
                form_secondary_abilities = []

                for ability in form_abilities:
                    if ability.startswith("h:"):
                        form_hidden_ability = ability[2:]
                    elif not form_primary_ability:
                        form_primary_ability = ability
                    else:
                        form_secondary_abilities.append(ability)

                form_secondary_abilities = ', '.join(form_secondary_abilities)

                egg_groups = form.get("eggGroups", extracted_data.get("egg_groups", []))
                if isinstance(egg_groups, list):
                    egg_groups = ', '.join(egg_groups)

                form_inserts.append((
                    int(extracted_data["dex_number"]),
                    extracted_data["pokemon_name"],
                    form_name,
                    form.get("primaryType", extracted_data.get("primary_type")),
                    form.get("secondaryType", extracted_data.get("secondary_type")),
                    egg_groups,
                    int(form.get("catchRate", extracted_data.get("catch_rate", 0))),
                    int(form.get("baseExperienceYield", extracted_data.get("base_experience_yield", 0))),
                    int(form.get("baseFriendship", extracted_data.get("base_friendship", 0))),
                    ', '.join(form.get("labels", [])),
                    form_primary_ability,
                    form_hidden_ability,
                    form_secondary_abilities,
                    float(form.get("height", extracted_data.get("height", 0.0))),
                    float(form.get("weight", extracted_data.get("weight", 0.0))),
                    json.dumps(form.get("base_stats", {})),
                    json.dumps(form)
                ))

            cursor.executemany('''
                INSERT INTO forms (
                    dex_number, pokemon_name, form_name, primary_type, secondary_type, egg_groups,
                    catch_rate, base_experience_yield, base_friendship, labels,
                    primary_ability, hidden_ability, secondary_abilities, height, weight,
                    base_stats, raw_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', form_inserts)

            # Insert evolutions data
            evolution_inserts = []
            for evolution in extracted_data.get("evolutions", []):
                evolution_inserts.append((
                    int(extracted_data["dex_number"]),
                    extracted_data["pokemon_name"],
                    evolution.get("evolves_to", "").capitalize(),
                    int(evolution.get("evolution_level", 0)) if evolution.get("evolution_level") is not None else None,
                    json.dumps(evolution.get("conditions", {}))
                ))

            cursor.executemany('''
                INSERT INTO evolutions (
                    dex_number, evolves_from, evolves_to, evolution_level, conditions
                ) VALUES (?, ?, ?, ?, ?)
            ''', evolution_inserts)

            # Insert moves data
            move_inserts = []
            for category, moves in extracted_data.get("moves", {}).items():
                for move in moves:
                    move_inserts.append((
                        int(extracted_data["dex_number"]),
                        category,
                        move
                    ))

            cursor.executemany('''
                INSERT INTO moves (
                    dex_number, category, move_name
                ) VALUES (?, ?, ?)
            ''', move_inserts)

            # Commit the transaction
            connection.commit()
            logging.info(f"Data for {extracted_data['pokemon_name']} (Dex {extracted_data['dex_number']}) inserted successfully.")
        except sqlite3.Error as e:
            logging.error(f"Database error while inserting data: {e}")
