// Backend API base URL
const API_BASE = "http://localhost:8000";

let analysisResult = null;
let extractedClauses = [];

function showAnalyzer() {
  document.getElementById("welcomePage").style.display = "none";
  document.getElementById("analyzerPage").style.display = "block";
}

function showWelcome() {
  document.getElementById("welcomePage").style.display = "block";
  document.getElementById("analyzerPage").style.display = "none";
  resetAnalyzer();
}

function resetAnalyzer() {
  document.getElementById("uploadSection").style.display = "block";
  document.getElementById("loadingSection").style.display = "none";
  document.getElementById("resultsSection").style.display = "none";
  document.getElementById("analyzeButton").style.display = "none";
  document.getElementById("fileInput").value = "";

  // Reset upload text
  const uploadText = document.querySelector(".upload-text p");
  uploadText.textContent =
    "Drag and drop your legal documents here or click to browse";
  uploadText.style.color = "white";
  uploadText.style.fontWeight = "normal";
}

function handleFileUpload(event) {
  const file = event.target.files[0];
  if (file) {
    const fileSize = file.size / (1024 * 1024); // Convert to MB
    if (fileSize > 25) {
      alert("File size must be less than 25MB");
      return;
    }

    const validTypes = ["application/pdf"];
    if (!validTypes.includes(file.type)) {
      alert("Please upload a PDF file");
      return;
    }

    document.getElementById("analyzeButton").style.display = "inline-block";

    // Update upload section to show file selected
    const uploadText = document.querySelector(".upload-text p");
    uploadText.textContent = `Selected: ${file.name}`;
    uploadText.style.color = "#4CAF50";
    uploadText.style.fontWeight = "600";
  }
}

async function analyzeDocument() {
  // Hide upload section and show loading
  document.getElementById("uploadSection").style.display = "none";
  document.getElementById("loadingSection").style.display = "block";
  document.getElementById("resultsSection").style.display = "none";

  const fileInput = document.getElementById("fileInput");
  const file = fileInput.files[0];
  if (!file) {
    alert("Please select a PDF file to analyze.");
    resetAnalyzer();
    return;
  }

  try {
    // 1. Upload PDF to backend and extract clauses
    const formData = new FormData();
    formData.append("file", file);
    const extractRes = await fetch(`${API_BASE}/extract_clauses/`, {
      method: "POST",
      body: formData,
    });
    if (!extractRes.ok) throw new Error("Failed to extract clauses from PDF.");
    const extractData = await extractRes.json();
    extractedClauses = extractData.clauses || [];

    // 2. For each clause, call /classify_clause/, /match_clause/, and /generate_explanation/
    const classifiedClauses = await Promise.all(
      extractedClauses.map(async (clause) => {
        let category = "Uncategorized", riskLevel = "Unknown", key_points = [], action_required = [], match = "", explanation = "";
        try {
          // Classification
          const form = new FormData();
          form.append("clause_text", clause.text);
          const res = await fetch(`${API_BASE}/classify_clause/`, {
            method: "POST",
            body: form,
          });
          if (res.ok) {
            const data = await res.json();
            category = data.category || category;
            riskLevel = data.risk_level || riskLevel;
            key_points = data.key_points || [];
            action_required = data.action_required || [];
          }
        } catch {}
        try {
          // Clause matching
          const form = new FormData();
          form.append("clause_text", clause.text);
          const res = await fetch(`${API_BASE}/match_clause/`, {
            method: "POST",
            body: form,
          });
          if (res.ok) {
            const data = await res.json();
            match = data.match || "";
          }
        } catch {}
        try {
          // Explanation
          const res = await fetch(`${API_BASE}/generate_explanation`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              text: clause.text,
              category: category,
              risk_level: riskLevel,
            }),
          });
          if (res.ok) {
            const data = await res.json();
            explanation = data.explanation || "";
          } else {
            const errorData = await res.json();
            if (errorData.explanation) {
                explanation = errorData.explanation; // Use backend's fallback explanation
            } else if (errorData.error) {
                explanation = `Error: ${errorData.error}`; // Display generic error
            } else {
                explanation = "Explanation unavailable.";
            }
          }
        } catch {}
        return {
          ...clause,
          category,
          riskLevel,
          keyPoints: key_points,
          actionRequired: action_required,
          match,
          explanation,
        };
      })
    );

    // 3. Calculate summary stats
    let highRisk = 0, mediumRisk = 0, lowRisk = 0;
    classifiedClauses.forEach((clause) => {
      if (clause.riskLevel === "High") highRisk++;
      if (clause.riskLevel === "Medium") mediumRisk++;
      if (clause.riskLevel === "Low") lowRisk++;
    });
    const summary = {
      totalClauses: classifiedClauses.length,
      overallRisk: highRisk > 0 ? "High" : mediumRisk > 0 ? "Medium" : lowRisk > 0 ? "Low" : "Unknown",
      highRiskClauses: highRisk,
      mediumRiskClauses: mediumRisk,
      lowRiskClauses: lowRisk,
    };

    // 4. Prepare analysisResult for dashboard and clause cards
    analysisResult = {
      summary,
      clauses: classifiedClauses.map((clause, idx) => ({
        title: cleanClauseTitle(clause.title),
        category: clause.category,
        riskLevel: clause.riskLevel,
        preview: clause.text.slice(0, 120) + (clause.text.length > 120 ? "..." : ""),
        keyPoints: clause.keyPoints,
        actionRequired: clause.actionRequired,
        explanation: truncateExplanation(clause.explanation),
      })),
    };

    // 5. Hide loading, show results
    document.getElementById("loadingSection").style.display = "none";
    document.getElementById("resultsSection").style.display = "block";
    populateDashboard();
    populateClauses();
    document.getElementById("resultsSection").scrollIntoView({ behavior: "smooth" });
  } catch (err) {
    document.getElementById("loadingSection").style.display = "none";
    alert("Error: " + err.message);
    resetAnalyzer();
  }
}

function populateDashboard() {
  const dashboard = document.getElementById("dashboard");
  const { summary } = analysisResult || { summary: {} };
  dashboard.innerHTML = `
                <div class="dashboard-card">
                    <div class="dashboard-value">${summary.totalClauses || 0}</div>
                    <div class="dashboard-label">Total Clauses</div>
                </div>
                <div class="dashboard-card">
                    <div class="dashboard-value">${summary.overallRisk || "-"}</div>
                    <div class="dashboard-label">Overall Risk</div>
                </div>
                <div class="dashboard-card">
                    <div class="dashboard-value">${summary.highRiskClauses || 0}</div>
                    <div class="dashboard-label">High Risk Clauses</div>
                </div>
            `;
}

function populateClauses() {
  const clausesGrid = document.getElementById("clausesGrid");
  const { clauses } = analysisResult || { clauses: [] };
  clausesGrid.innerHTML = clauses
    .map(
      (clause, index) => `
                <div class="clause-card" onclick="toggleClauseDetails(${index})">
                    <div class="clause-header">
                        <div>
                            <div class="clause-title">${clause.title}</div>
                            <div class="clause-category">${clause.category}</div>
                        </div>
                        <div class="risk-badge risk-${clause.riskLevel.toLowerCase()}">
                            ${clause.riskLevel} Risk
                        </div>
                    </div>
                    <div class="clause-preview">${clause.preview}</div>
                    <div class="clause-details" id="details-${index}">
                        <div class="details-section">
                            <div class="details-title">
                                <i class="fas fa-key"></i>
                                Key Points
                            </div>
                            <ul class="details-list">
                                ${clause.keyPoints
                                  .map((point) => `<li>${point}</li>`)
                                  .join("")}
                            </ul>
                        </div>
                        <div class="details-section">
                            <div class="details-title">
                                <i class="fas fa-exclamation-triangle"></i>
                                Actions Required
                            </div>
                            <ul class="details-list">
                                ${clause.actionRequired
                                  .map((action) => `<li>${action}</li>`)
                                  .join("")}
                            </ul>
                        </div>
                        <div class="details-section">
                            <div class="details-title">
                                <i class="fas fa-lightbulb"></i>
                                Explanation
                            </div>
                            <p class="details-text">
                                ${clause.explanation ||
                                  "No explanation available for this clause."}
                            </p>
                        </div>
                    </div>
                </div>
            `
    )
    .join("");
}

function toggleClauseDetails(index) {
  const details = document.getElementById(`details-${index}`);
  const isActive = details.classList.contains("active");

  // Close all other details
  document.querySelectorAll(".clause-details").forEach((detail) => {
    detail.classList.remove("active");
  });

  // Toggle current details
  if (!isActive) {
    details.classList.add("active");
    details.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }
}

// Add some interactive elements on page load
window.addEventListener("load", function () {
  // Add subtle animations to feature cards
  const featureCards = document.querySelectorAll(".feature-card");
  featureCards.forEach((card, index) => {
    setTimeout(() => {
      card.style.opacity = "1";
      card.style.transform = "translateY(0)";
    }, index * 200);
  });
});

function cleanClauseTitle(title) {
  return title.replace(/^\s*\d+\.?\s*/, '');
}

function truncateExplanation(explanation, maxLength = 350) {
  if (explanation.length <= maxLength) {
    return explanation;
  }
  return explanation.substring(0, explanation.lastIndexOf(' ', maxLength)) + '...';
}
