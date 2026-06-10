"""
app.py
Flask REST API for the Farm Score Project.
"""

import uuid
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from farmscore import calculate_score

app = Flask(__name__)
CORS(app)  # Allow requests from the frontend

# In-memory store for scores (replace with a database for production)
score_store: dict = {}


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

    Required JSON body fields:
        - farm_name        (str)
        - soil_health      (float, 0–10)
        - water_usage_efficiency (float, 0–10)
        - biodiversity_score     (float, 0–10)
        - irrigation_type  (str): drip | sprinkler | flood | rainfed
        - crop_type        (str)

    Optional:
        - area_hectares    (float)
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
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 422

    result = calculate_score(data)

    # Persist with a unique ID so the score can be retrieved later
    record_id = str(uuid.uuid4())
    score_store[record_id] = result

    return jsonify({"id": record_id, **result}), 201


@app.get("/score/<record_id>")
def get_score(record_id: str):
    """Retrieve a previously calculated score by its ID."""
    record = score_store.get(record_id)
    if record is None:
        return jsonify({"error": "Score record not found."}), 404
    return jsonify({"id": record_id, **record})


@app.get("/scores")
def list_scores():
    """Return all stored scores (useful for development/debugging)."""
    return jsonify(
        [{"id": k, **v} for k, v in score_store.items()]
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True, port=5000)
