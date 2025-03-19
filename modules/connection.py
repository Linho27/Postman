#LEDs controlling module

# Libraries import
import requests
from flask import Flask, jsonify, request


#This module will include necessary stuff for connection (maybe also comparison) with the mts

app = Flask(__name__) 

@app.route('/')
def home():
    return "Hello, World!"

@app.route('/data', methods=['GET'])
def get_data():
    data = {
        "id": 1,
        "name": "Example",
        "description": "This is an example data."
    }
    return jsonify(data)

@app.route('/data', methods=['POST'])
def create_data():
    new_data = request.get_json()
    return jsonify(new_data), 201

if __name__ == '__main__':
    app.run(debug=True)