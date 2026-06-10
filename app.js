/**
 * app.js
 * FarmScore Frontend Logic
 */

const API_BASE = "https://farm-score-project.onrender.com";

// Slider Value Update
const sliders = [
  { id: "soil_health", valId: "soil_val" },
  { id: "water_usage_efficiency", valId: "water_val" },
  { id: "biodiversity_score", valId: "bio_val" }
];

sliders.forEach(({ id, valId }) => {
  const slider = document.getElementById(id);
  const display = document.getElementById(valId);

  if (slider && display) {
    slider.addEventListener("input", () => {
      display.textContent = slider.value;
    });
  }
});

// Submit Form
async function submitFarm() {

  clearError();

  const payload = {
    farm_name: document.getElementById("farm_name").value,
    crop_type: document.getElementById("crop_type").value,
    area_hectares: parseFloat(document.getElementById("area_hectares").value) || 0,
    irrigation_type: document.getElementById("irrigation_type").value,
    soil_health: parseFloat(document.getElementById("soil_health").value) || 0,
    water_usage_efficiency:
      parseFloat(document.getElementById("water_usage_efficiency").value) || 0,
    biodiversity_score:
      parseFloat(document.getElementById("biodiversity_score").value) || 0
  };

  const btn = document.getElementById("submit-btn");

  btn.disabled = true;
  btn.innerText = "Calculating...";

  try {

    const response = await fetch(`${API_BASE}/score`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Server Error");
    }

    renderResults(data);

  } catch (err) {

    showError(err.message);

  } finally {

    btn.disabled = false;
    btn.innerText = "Calculate Score";
  }
}

// Render Results
function renderResults(data) {

  document.getElementById("result-section").style.display = "block";

  document.getElementById("farm-name-result").innerText =
    data.farm_name;

  document.getElementById("score-result").innerText =
    data.total_score;

  document.getElementById("grade-result").innerText =
    data.grade;

  // Breakdown
  const breakdownDiv = document.getElementById("breakdown");

  breakdownDiv.innerHTML = "";

  for (const key in data.breakdown) {

    breakdownDiv.innerHTML += `
      <div class="score-item">
        <strong>${formatLabel(key)}</strong>
        <span>${data.breakdown[key]}</span>
      </div>
    `;
  }

  // Recommendations
  const recList = document.getElementById("recommendations");

  recList.innerHTML = "";

  data.recommendations.forEach(rec => {

    recList.innerHTML += `<li>${rec}</li>`;

  });
}

// Helpers
function formatLabel(text) {
  return text
    .replace(/_/g, " ")
    .replace(/\b\w/g, c => c.toUpperCase());
}

function showError(message) {

  const err = document.getElementById("error-msg");

  err.innerText = message;
  err.style.display = "block";
}

function clearError() {

  const err = document.getElementById("error-msg");

  err.innerText = "";
  err.style.display = "none";
}
