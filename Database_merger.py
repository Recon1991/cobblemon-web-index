import sqlite3

# Connect to the base and shiny databases
conn_base = sqlite3.connect('pokemon_palettes_base.db')
cursor_base = conn_base.cursor()

conn_shiny = sqlite3.connect('pokemon_palettes_shiny.db')
cursor_shiny = conn_shiny.cursor()

# Create a new connection for the merged database (or merge into one of the existing ones)
conn_merged = sqlite3.connect('pokemon_palettes_merged.db')
cursor_merged = conn_merged.cursor()

# Create the merged table if it doesn't exist
cursor_merged.execute('''
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

# Copy data from the base database to the merged database
cursor_base.execute('SELECT * FROM pokemon_colors')
base_rows = cursor_base.fetchall()
for row in base_rows:
    cursor_merged.execute('''
        INSERT OR REPLACE INTO pokemon_colors (shiny, dex_number, pokemon_name, form_name, color1, color2, color3, color4, color5, color6, color7, color8, color9)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', row)

# Copy data from the shiny database to the merged database
cursor_shiny.execute('SELECT * FROM pokemon_colors')
shiny_rows = cursor_shiny.fetchall()
for row in shiny_rows:
    cursor_merged.execute('''
        INSERT OR REPLACE INTO pokemon_colors (shiny, dex_number, pokemon_name, form_name, color1, color2, color3, color4, color5, color6, color7, color8, color9)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', row)

# Commit changes and close all connections
conn_merged.commit()
conn_base.close()
conn_shiny.close()
conn_merged.close()

print("Databases merged successfully!")
