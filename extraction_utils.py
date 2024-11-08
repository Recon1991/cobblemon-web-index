import json
import sqlite3
import configparser
import logging
from db_utils import initialize_database, insert_pokemon_data
from species_info_extractor import extract_species_info
from contextlib import closing
import zipfile
import os
import shutil

def extract_from_archives(archives_dirs, extracted_dir, target_directory='data/cobblemon/species', overwrite=True):
    """
    Extract specific directories from zip/jar files in the archives
    Only extracts the target directory (e.g., 'data/cobblemon/species').
    Tracks the original archive for each extracted file.
    """

    # Remove existing extracted directory if needed
    if overwrite and os.path.exists(extracted_dir):
        shutil.rmtree(extracted_dir)

    os.makedirs(extracted_dir, exist_ok=True)

    # Dictionary to store the origin of extracted files
    extracted_files_mapping = {}

    for archives_dir in archives_dirs:
        for archive_name in os.listdir(archives_dir):
            if archive_name.endswith(('.zip', '.jar')):
                archive_path = os.path.join(archives_dir, archive_name)
                with zipfile.ZipFile(archive_path, 'r') as zip_file:
                    for file_info in zip_file.infolist():
                        # Ensure only files from the exact target directory are extracted
                        if file_info.filename.startswith(target_directory + '/') and file_info.filename.endswith('.json'):
                            extracted_path = zip_file.extract(file_info, extracted_dir)
                            with open(os.path.join(extracted_dir, file_info.filename), 'r', encoding='utf-8-sig') as f:  # Use utf-8-sig to handle BOM
                                f.read()  # Ensure the file is readable with the correct encoding
                            extracted_files_mapping[os.path.abspath(extracted_path)] = archive_name
                            logging.info(f"Extracted {file_info.filename} from {archive_name}")

    return extracted_files_mapping
