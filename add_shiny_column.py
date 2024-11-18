import sqlite3
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Connect to the existing SQLite3 database
conn = sqlite3.connect('pokemon_palettes.db')
cursor = conn.cursor()

# Try to add a new 'shiny' column to the existing table
try:
    cursor.execute("ALTER TABLE pokemon_colors ADD COLUMN shiny BOOLEAN DEFAULT 0")
    print(Fore.GREEN + "Successfully added 'shiny' column to the existing table.", flush=True)
except sqlite3.OperationalError as e:
    if 'duplicate column name' in str(e).lower():
        print(Fore.YELLOW + "The 'shiny' column already exists.", flush=True)
    else:
        print(Fore.RED + f"Failed to add 'shiny' column. Error: {str(e)}", flush=True)

# Commit changes and close the connection
conn.commit()
conn.close()

print(Fore.CYAN + "Database update complete.", flush=True)
