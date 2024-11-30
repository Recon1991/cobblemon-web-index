from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

@app.route('/api/hello', methods=['GET'])
def hello_world():
    return jsonify({"message": "Hello, Cobblemon!"})

@app.route('/api/pokemon', methods=['GET'])
def get_pokemon():
    return jsonify([
        {"dex_number": 1, "pokemon_name": "Bulbasaur", "primary_type": "Grass", "secondary_type": "Poison"},
        {"dex_number": 2, "pokemon_name": "Ivysaur", "primary_type": "Grass", "secondary_type": "Poison"}
    ])

if __name__ == '__main__':
    app.run(debug=True)