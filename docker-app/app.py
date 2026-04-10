from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>Flask app running in Docker</h1><p>Try <a href='/api'>/api</a></p>"

@app.route("/api")
def api():
    return jsonify({
        "status": "ok",
        "message": "Hello from Flask + Docker",
        "env": os.getenv("APP_ENV", "development")
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
