/* Galaxy Desk JavaScript */
window.galaxy = window.galaxy || {};

// ── Toast ───────────────────────────────────────────────
galaxy.toast = function (message, opts) {
  opts = opts || {};
  const tone = opts.tone || "info";
  const duration = opts.duration || 3000;
  const container = document.getElementById("galaxy-toast-container");
  if (!container) return;
  const el = document.createElement("div");
  el.className = "galaxy-toast galaxy-toast-" + tone;
  el.textContent = message;
  container.appendChild(el);
  setTimeout(() => { el.classList.add("galaxy-toast-exit"); setTimeout(() => el.remove(), 300); }, duration);
};

// ── Confirm Dialog ─────────────────────────────────────
galaxy.confirm = function (message, opts) {
  opts = opts || {};
  const tone = opts.tone || "warning";
  return new Promise((resolve) => {
    const backdrop = document.createElement("div");
    backdrop.className = "galaxy-backdrop";
    backdrop.innerHTML =
      '<div class="galaxy-modal galaxy-modal-' + tone + '">' +
        '<div class="galaxy-modal-body"><p>' + message + '</p></div>' +
        '<div class="galaxy-modal-footer">' +
          '<button class="galaxy-btn galaxy-btn-ghost galaxy-btn-neutral galaxy-btn-sm" data-cancel>Cancel</button>' +
          '<button class="galaxy-btn galaxy-btn-solid galaxy-btn-' + tone + ' galaxy-btn-sm" data-confirm>' + (opts.confirmText || "Confirm") + '</button>' +
        '</div>' +
      '</div>';
    document.body.appendChild(backdrop);
    backdrop.querySelector("[data-cancel]").onclick = () => { backdrop.remove(); resolve(false); };
    backdrop.querySelector("[data-confirm]").onclick = () => { backdrop.remove(); resolve(true); };
    backdrop.onclick = (e) => { if (e.target === backdrop) { backdrop.remove(); resolve(false); } };
  });
};

// ── Modal ───────────────────────────────────────────────
galaxy.modal = {
  open: function (id) {
    const el = document.getElementById(id);
    if (el) el.classList.add("galaxy-modal-open");
  },
  close: function (id) {
    const el = document.getElementById(id);
    if (el) el.classList.remove("galaxy-modal-open");
    else document.querySelectorAll(".galaxy-backdrop").forEach(b => b.remove());
  }
};

// ── Theme Switcher ──────────────────────────────────────
galaxy.theme = {
  toggle: function () {
    document.documentElement.classList.toggle("dark");
    const mode = document.documentElement.classList.contains("dark") ? "dark" : "light";
    localStorage.setItem("galaxy-theme", mode);
  },
  init: function () {
    const saved = localStorage.getItem("galaxy-theme");
    if (saved === "dark") document.documentElement.classList.add("dark");
  }
};

// ── Init on load ────────────────────────────────────────
document.addEventListener("DOMContentLoaded", function () {
  galaxy.theme.init();
  // Toast container
  if (!document.getElementById("galaxy-toast-container")) {
    const c = document.createElement("div");
    c.id = "galaxy-toast-container";
    c.style.cssText = "position:fixed;top:1rem;right:1rem;z-index:9999;display:flex;flex-direction:column;gap:0.5rem";
    document.body.appendChild(c);
  }
  // Theme toggle buttons
  document.querySelectorAll("[data-toggle-theme]").forEach(function (btn) {
    btn.onclick = function (e) { e.preventDefault(); galaxy.theme.toggle(); };
  });
  // Modal close buttons
  document.querySelectorAll("[data-modal-close]").forEach(function (btn) {
    btn.onclick = function () { galaxy.modal.close(btn.dataset.modalClose); };
  });
});
