from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

@app.route('/api/hello', methods=['GET'])
def hello_world():
    return jsonify({"message": "Hello, Cobblemon!"})

if __name__ == '__main__':
    app.run(debug=True)