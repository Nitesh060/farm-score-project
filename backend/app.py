"""
app.py
Flask REST API for the Farm Score Project.
"""

import os
import uuid
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from farmscore import calculate_score

# Get project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Tell Flask where the HTML/CSS/JS files are
app = Flask(
    __name__,
    template_folder=BASE_DIR,
    static_folder=BASE_DIR,
    static_url_path=""
)

CORS(app)

# In-memory store for scores
score_store = {}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


@app.post("/score")
def score_farm():
    """
    Accept farm data and return a calculated score.
    """

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    required_fields = [
        "farm_name",
        "soil_health",
        "water_usage_efficiency",
        "biodiversity_score",
        "irrigation_type",
        "crop_type",
    ]

    missing = [f for f in required_fields if f not in data]

    if missing:
        return jsonify(
            {"error": f"Missing required fields: {', '.join(missing)}"}
        ), 422

    result = calculate_score(data)

    record_id = str(uuid.uuid4())
    score_store[record_id] = result

    return jsonify({"id": record_id, **result}), 201


@app.get("/score/<record_id>")
def get_score(record_id):
    record = score_store.get(record_id)

    if record is None:
        return jsonify({"error": "Score record not found."}), 404

    return jsonify({"id": record_id, **record})


@app.get("/scores")
def list_scores():
    return jsonify(
        [{"id": k, **v} for k, v in score_store.items()]
    )


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
