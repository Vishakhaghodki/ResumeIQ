const COLORS = { good: "#16a34a", warn: "#f59e0b", bad: "#ef4444", primary: "#5b5bf0", purple: "#8b5cf6", grey: "#cbd0e6" };
const scoreColor = v => (v >= 75 ? COLORS.good : v >= 50 ? COLORS.warn : COLORS.bad);
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();

Chart.defaults.color = css("--muted") || "#6b7190";
Chart.defaults.font.family = "system-ui, 'Segoe UI', sans-serif";
Chart.defaults.maintainAspectRatio = false;

const centerText = {
  id: "centerText",
  afterDraw(chart, _args, opts) {
    if (!opts || opts.text === undefined) return;
    const { ctx, chartArea: { left, right, top, bottom } } = chart;
    ctx.save();
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillStyle = css("--text") || "#000";
    ctx.font = "bold 30px system-ui";
    ctx.fillText(opts.text, (left + right) / 2, (top + bottom) / 2);
    ctx.restore();
  },
};

function gauge(id, value) {
  new Chart(document.getElementById(id), {
    type: "doughnut",
    data: { labels: ["Score", "Remaining"], datasets: [{ data: [value, 100 - value], backgroundColor: [scoreColor(value), COLORS.grey], borderWidth: 0 }] },
    options: { cutout: "76%", plugins: { legend: { display: false }, tooltip: { enabled: false }, centerText: { text: Math.round(value) } } },
    plugins: [centerText],
  });
}

function emptyState(canvasId, msg) {
  const canvas = document.getElementById(canvasId);
  canvas.style.display = "none";
  const note = canvas.parentElement.nextElementSibling;
  if (note && note.classList.contains("chart-empty")) { note.textContent = msg; note.style.display = "block"; }
}

function horizontalBar(id, labels, values, color, xLabel) {
  new Chart(document.getElementById(id), {
    type: "bar",
    data: { labels, datasets: [{ data: values, backgroundColor: color, borderRadius: 6 }] },
    options: { indexAxis: "y", plugins: { legend: { display: false } },
      scales: { x: { beginAtZero: true, ticks: { precision: 0 }, title: { display: !!xLabel, text: xLabel } }, y: { grid: { display: false } } } },
  });
}

function trendChart(id, trend) {
  return new Chart(document.getElementById(id), {
    type: "line",
    data: {
      labels: trend.map(t => t.label),
      datasets: [
        { label: "Match score", data: trend.map(t => t.match), borderColor: COLORS.primary, backgroundColor: COLORS.primary + "22", tension: .3, fill: true, pointRadius: 4 },
        { label: "ATS score", data: trend.map(t => t.ats), borderColor: COLORS.good, tension: .3, pointRadius: 4 },
      ],
    },
    options: { interaction: { mode: "index", intersect: false },
      scales: { y: { min: 0, max: 100 }, x: { ticks: { maxRotation: 40, autoSkip: true } } },
      plugins: { legend: { position: "bottom" } } },
  });
}

/* ---------- Result page ---------- */
function renderResultCharts(a) {
  gauge("matchChart", a.match_score);
  gauge("atsChart", a.ats_score);

  new Chart(document.getElementById("breakdownChart"), {
    type: "bar",
    data: { labels: ["Skills", "Keywords", "Similarity", "ATS"],
      datasets: [{ data: [a.skill_score, a.keyword_score, a.similarity_score, a.ats_score],
        backgroundColor: [COLORS.primary, COLORS.purple, "#06b6d4", COLORS.good], borderRadius: 8 }] },
    options: { plugins: { legend: { display: false } }, scales: { y: { min: 0, max: 100 }, x: { grid: { display: false } } } },
  });

  const matched = a.matched_skills.length, missing = a.missing_skills.length;
  if (matched + missing === 0) {
    emptyState("skillChart", "No recognised technical skills were found in the job description.");
  } else {
    new Chart(document.getElementById("skillChart"), {
      type: "doughnut",
      data: { labels: ["Matched skills", "Missing skills"], datasets: [{ data: [matched, missing], backgroundColor: [COLORS.good, COLORS.bad], borderWidth: 0 }] },
      options: { cutout: "62%", plugins: { legend: { position: "bottom" } } },
    });
  }

  if (!missing) emptyState("missingChart", "🎉 No missing skills detected.");
  else {
    const top = a.missing_skills.slice(0, 10);
    horizontalBar("missingChart", top.map(m => m.skill), top.map(m => m.mentions), COLORS.bad, "Mentions in job description");
  }
}

/* ---------- Dashboard ---------- */
async function renderDashboard() {
  const s = await apiFetch("/api/stats");
  document.getElementById("stTotal").textContent = s.total;
  document.getElementById("stMatch").textContent = s.avg_match;
  document.getElementById("stAts").textContent = s.avg_ats;
  document.getElementById("stBest").textContent = s.best_match;

  if (!s.total) {
    document.getElementById("dashEmpty").style.display = "block";
    document.getElementById("dashCharts").style.display = "none";
    return;
  }
  let trend = trendChart("trendChart", s.trend);
  document.getElementById("range").addEventListener("change", e => {
    const n = e.target.value === "all" ? s.trend.length : parseInt(e.target.value, 10);
    const slice = s.trend.slice(-n);
    trend.data.labels = slice.map(t => t.label);
    trend.data.datasets[0].data = slice.map(t => t.match);
    trend.data.datasets[1].data = slice.map(t => t.ats);
    trend.update();
  });

  gauge("avgAtsChart", s.avg_ats);
  new Chart(document.getElementById("avgChart"), {
    type: "bar",
    data: { labels: Object.keys(s.averages), datasets: [{ data: Object.values(s.averages), backgroundColor: [COLORS.primary, COLORS.purple, "#06b6d4", COLORS.good], borderRadius: 8 }] },
    options: { plugins: { legend: { display: false } }, scales: { y: { min: 0, max: 100 }, x: { grid: { display: false } } } },
  });
  new Chart(document.getElementById("distChart"), {
    type: "doughnut",
    data: { labels: s.distribution.labels, datasets: [{ data: s.distribution.values, backgroundColor: [COLORS.bad, COLORS.warn, "#84cc16", COLORS.good], borderWidth: 0 }] },
    options: { cutout: "55%", plugins: { legend: { position: "bottom" } } },
  });
  if (!s.top_missing.length) emptyState("topMissingChart", "No missing skills across your analyses. Great!");
  else horizontalBar("topMissingChart", s.top_missing.map(m => m.skill), s.top_missing.map(m => m.count), COLORS.bad, "Analyses missing this skill");
}
