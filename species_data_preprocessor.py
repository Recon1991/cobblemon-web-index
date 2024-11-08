import os
import json
import sqlite3
import configparser
import logging
from db_utils import initialize_database, insert_pokemon_data
from extraction_utils import extract_from_archives
from species_info_extractor import extract_species_info
from contextlib import closing

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load configuration from config file
config = configparser.ConfigParser()
config.read('config.ini')

# Load archive directories from config file
mods_directory = os.path.expandvars(config.get('SETTINGS', 'MODS_DIR', fallback='zip_archives'))
resourcepacks_directory = os.path.expandvars(config.get('SETTINGS', 'RESOURCEPACKS_DIR', fallback='zip_archives'))

# Configure skipped entries log file
skipped_entries_log = 'skipped_entries.log'

# Clear previous skipped entries log
if os.path.exists(skipped_entries_log):
    os.remove(skipped_entries_log)

def main():
    # Initialize database
    initialize_database()

    # Extract archives and build file mapping
    extracted_files_mapping = extract_from_archives([mods_directory, resourcepacks_directory], './data/extracted', target_directory='data/cobblemon/species')

    # Process and insert data into the database
    with closing(sqlite3.connect('pokemon_data.db')) as connection:
        for file_path, archive_name in extracted_files_mapping.items():
            try:
                with open(file_path, 'r', encoding='utf-8-sig') as f:  # Use utf-8-sig to handle BOM
                    species_data = json.load(f)
                    extracted_data = extract_species_info(species_data)

                    # Skip entries with invalid dex numbers
                    if extracted_data is None or extracted_data.get("dex_number") == "Unknown":
                        logging.error(f"Skipping entry with missing dex number for file: {file_path}")
                        with open(skipped_entries_log, 'a') as skipped_log:
                            skipped_log.write(f"Skipped entry: {file_path}\n")
                        continue

                    extracted_data["raw_data"] = species_data if species_data else {}
                    insert_pokemon_data(extracted_data, connection)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                logging.error(f"Error reading file {file_path}: {e}")

if __name__ == "__main__":
    main()
