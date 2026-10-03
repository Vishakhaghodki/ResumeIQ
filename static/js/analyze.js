(function () {
  const MAX = 5 * 1024 * 1024;
  const form = document.getElementById("analyzeForm");
  const drop = document.getElementById("dropzone");
  const input = document.getElementById("resume");
  const label = document.getElementById("fileLabel");
  const jd = document.getElementById("job_description");
  const count = document.getElementById("jdCount");
  const errorBox = document.getElementById("formError");
  const overlay = document.getElementById("overlay");
  const btn = document.getElementById("submitBtn");

  function showError(msg) { errorBox.textContent = msg; errorBox.className = "alert error"; }
  function clearError() { errorBox.className = "alert"; errorBox.textContent = ""; }

  function showFile() {
    const f = input.files[0];
    label.textContent = f ? "📄 " + f.name + " (" + (f.size / 1024).toFixed(0) + " KB)"
                          : "Click to choose a PDF or drag it here";
  }

  drop.addEventListener("click", () => input.click());
  input.addEventListener("change", showFile);
  ["dragenter", "dragover"].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.add("drag"); }));
  ["dragleave", "drop"].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.remove("drag"); }));
  drop.addEventListener("drop", e => {
    if (e.dataTransfer.files.length) { input.files = e.dataTransfer.files; showFile(); }
  });
  jd.addEventListener("input", () => { count.textContent = jd.value.length + " / 15000"; });

  form.addEventListener("submit", async e => {
    e.preventDefault();
    clearError();
    const f = input.files[0];
    if (!f) return showError("Please choose a PDF resume.");
    if (!f.name.toLowerCase().endsWith(".pdf")) return showError("Only PDF files are supported.");
    if (f.size > MAX) return showError("File too large. Maximum size is 5 MB.");
    if (jd.value.trim().length < 50) return showError("Job description must be at least 50 characters.");

    overlay.classList.add("show");
    btn.disabled = true;
    try {
      const data = await apiFetch("/api/analyze", { method: "POST", body: new FormData(form) });
      window.location.href = data.redirect;
    } catch (err) {
      overlay.classList.remove("show");
      btn.disabled = false;
      showError(err.message);
    }
  });
})();
