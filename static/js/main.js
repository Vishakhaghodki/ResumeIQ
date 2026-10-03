(function () {
  const toggle = document.getElementById("navToggle");
  const links = document.getElementById("navLinks");
  if (toggle) toggle.addEventListener("click", () => links.classList.toggle("open"));
})();

function toast(message) {
  const el = document.getElementById("toast");
  el.textContent = message;
  el.classList.add("show");
  setTimeout(() => el.classList.remove("show"), 2800);
}

async function apiFetch(url, options) {
  const res = await fetch(url, options);
  let data = {};
  try { data = await res.json(); } catch (_) { /* non-JSON response */ }
  if (!res.ok) throw new Error(data.error || "Request failed (" + res.status + ")");
  return data;
}
