from flask import Flask, render_template, jsonify
import subprocess
import pymongo
from datetime import datetime

app = Flask(__name__)

# MongoDB setup
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client.Last

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch', methods=['GET'])
def fetch_trends():
    # Run scraper
    try:
        subprocess.run(["python3", "main.py"], check=True)
    except Exception as e:
        return jsonify({"error": f"Error running scraper: {e}"}), 500

    # Fetch the latest record from MongoDB
    latest_record = db.trends.find_one(sort=[("timestamp", -1)])

    if not latest_record:
        return jsonify({"response": {"trends": [], "proxy_ip": "", "unique_id": ""}}), 200

    # Constructing the trends response
    trends = []
    for i in range(1, 6):  # Loop through trend_1 to trend_5
        trend_key = f"trend_{i}"
        if trend_key in latest_record:
            trend_description = latest_record[trend_key].replace('\n', ' ')  # Clean up the description
            trend_display = f"{i}- {trend_description}"  # Part 1 format
            trends.append([trend_display])  # For Part 1 format

    # Response data formatting
    response_data = {
        "timestamp": latest_record["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
        "trends": trends,
        "unique_id": latest_record["unique_id"],
        "proxy_ip": latest_record["proxy_ip"],
    }

    return jsonify({"response": response_data})


if __name__ == "__main__":
    app.run(debug=True)
