from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/health")
def health():
    response = jsonify(health="healthy")
    response.status_code = 200
    return response
