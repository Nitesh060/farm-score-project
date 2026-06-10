/**
 * app.js
 * Frontend logic for Farm Score Project.
 */

const API_BASE = "https://farm-score-project.onrender.com";

// ── Slider live-update ──────────────────────────────────────
const sliders = [
  { id: "soil_health",           valId: "soil_val"  },
  { id: "water_usage_efficiency", valId: "water_val" },
  { id: "biodiversity_score",    valId: "bio_val"   },
];

sliders.forEach(({ id, valId }) => {
  const slider = document.getElementById(id);
  const display = document.getElementById(valId);
  slider.addEventListener("input", () => {
    display.textContent = slider.value;
  });
});

// ── Submit ──────────────────────────────────────────────────
async function submitFarm() {
  clearError();

  const payload = {
    farm_name:              val("farm_name"),
    crop_type:              val("crop_type"),
    area_hectares:          numVal("area_hectares"),
    irrigation_type:        val("irrigation_type"),
    soil_health:            numVal("soil_health"),
    water_usage_efficiency: numVal("water_usage_efficiency"),
    biodiversity_score:     numVal("biodiversity_score"),
  };

  // Basic validation
  const required = ["farm_name", "crop_type", "irrigation_type"];
  const missing = required.filter((k) => !payload[k]);
  if (missing.length) {
    showError("Please fill in: " + missing.map(humanise).join(", "));
    return;
  }

  const btn = document.getElementById("submit-btn");
  btn.textContent = "Calculating…";
  btn.disabled = true;

  try {
    const res = await fetch(`${API_BASE}/score`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.error || "Server error");
    }

    renderResults(data);
  } catch (err) {
    showError("Could not reach the API. Is the backend running? (" + err.message + ")");
  } finally {
    btn.textContent = "Calculate Score";
    btn.disabled = false;
  }
}

// ── Render ──────────────────────────────────────────────────
function renderResults(data) {
  document.getElementById("form-section").classList.add("hidden");
  const section = document.getElementById("result-section");
  section.classList.remove("hidden");

  document.getElementById("grade-badge").textContent   = data.grade;
  document.getElementById("total-score").textContent   = data.total_score;
  document.getElementById("result-farm-name").textContent = data.farm_name;

  // Breakdown bars
  const maxPoints = { soil_health: 30, water_efficiency: 25, biodiversity: 20, practices: 25 };
  const labels     = {
    soil_health:      "Soil Health",
    water_efficiency: "Water Efficiency",
    biodiversity:     "Biodiversity",
    practices:        "Sustainable Practices",
  };

  const breakdownEl = document.getElementById("breakdown");
  breakdownEl.innerHTML = "";

  Object.entries(data.breakdown).forEach(([key, score]) => {
    const max   = maxPoints[key] || 25;
    const pct   = Math.min((score / max) * 100, 100).toFixed(1);
    const row   = document.createElement("div");
    row.className = "bar-row";
    row.innerHTML = `
      <div class="bar-label">
        <span>${labels[key] || key}</span>
        <span>${score} / ${max}</span>
      </div>
      <div class="bar-track">
        <div class="bar-fill" style="width: 0%" data-pct="${pct}"></div>
      </div>`;
    breakdownEl.appendChild(row);
  });

  // Animate bars after paint
  requestAnimationFrame(() => {
    document.querySelectorAll(".bar-fill").forEach((bar) => {
      bar.style.width = bar.dataset.pct + "%";
    });
  });

  // Recommendations
  const recList = document.getElementById("rec-list");
  recList.innerHTML = "";
  (data.recommendations || []).forEach((rec) => {
    const li = document.createElement("li");
    li.textContent = rec;
    recList.appendChild(li);
  });
}

// ── Reset ───────────────────────────────────────────────────
function resetForm() {
  document.getElementById("result-section").classList.add("hidden");
  document.getElementById("form-section").classList.remove("hidden");
}

// ── Helpers ─────────────────────────────────────────────────
function val(id)    { return document.getElementById(id)?.value?.trim() ?? ""; }
function numVal(id) { return parseFloat(document.getElementById(id)?.value) || 0; }

function showError(msg) {
  const el = document.getElementById("error-msg");
  el.textContent = msg;
  el.classList.remove("hidden");
}

function clearError() {
  const el = document.getElementById("error-msg");
  el.textContent = "";
  el.classList.add("hidden");
}

function humanise(key) {
  return key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}
