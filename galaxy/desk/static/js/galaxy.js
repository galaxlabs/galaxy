/* Galaxy Desk JavaScript */
window.galaxy = window.galaxy || {};

// ── Init on DOM ready ──
document.addEventListener("DOMContentLoaded", function () {
  galaxy.theme.init();
  galaxy.initCommandPalette();
  galaxy.initUserMenu();
  galaxy.initSidebar();
  galaxy.initHTMX();
  galaxy.initToasts();
  galaxy.initNavActive();
});

// ── Toast ──
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
  setTimeout(function () {
    el.classList.add("galaxy-toast-exit");
    setTimeout(function () { el.remove(); }, 300);
  }, duration);
};

galaxy.initToasts = function () {
  if (!document.getElementById("galaxy-toast-container")) {
    var c = document.createElement("div");
    c.id = "galaxy-toast-container";
    c.style.cssText = "position:fixed;top:1rem;right:1rem;z-index:9999;display:flex;flex-direction:column;gap:0.5rem;pointer-events:none";
    document.body.appendChild(c);
  }
};

// ── Confirm Dialog ──
galaxy.confirm = function (message, opts) {
  opts = opts || {};
  var tone = opts.tone || "warning";
  return new Promise(function (resolve) {
    var backdrop = document.createElement("div");
    backdrop.className = "galaxy-backdrop";
    backdrop.style.display = "flex";
    backdrop.innerHTML =
      '<div class="galaxy-modal galaxy-modal-' + tone + '" style="max-width:24rem">' +
        '<div class="galaxy-modal-body"><p>' + message + '</p></div>' +
        '<div class="galaxy-modal-footer">' +
          '<button class="galaxy-btn galaxy-btn-ghost galaxy-btn-neutral galaxy-btn-sm" data-cancel>Cancel</button>' +
          '<button class="galaxy-btn galaxy-btn-solid galaxy-btn-' + tone + ' galaxy-btn-sm" data-confirm>' + (opts.confirmText || "Confirm") + '</button>' +
        '</div>' +
      '</div>';
    document.body.appendChild(backdrop);
    backdrop.querySelector("[data-cancel]").onclick = function () { backdrop.remove(); resolve(false); };
    backdrop.querySelector("[data-confirm]").onclick = function () { backdrop.remove(); resolve(true); };
    backdrop.onclick = function (e) { if (e.target === backdrop) { backdrop.remove(); resolve(false); } };
  });
};

// ── Modal ──
galaxy.modal = {
  open: function (id) {
    var el = document.getElementById(id);
    if (el) {
      el.style.display = "flex";
      el.classList.add("galaxy-modal-open");
    }
  },
  close: function (id) {
    var el = document.getElementById(id);
    if (el) { el.style.display = "none"; el.classList.remove("galaxy-modal-open"); }
    else {
      document.querySelectorAll(".galaxy-backdrop").forEach(function (b) { b.remove(); });
    }
  }
};

// ── Theme ──
galaxy.theme = {
  toggle: function () {
    document.documentElement.classList.toggle("dark");
    var mode = document.documentElement.classList.contains("dark") ? "dark" : "light";
    localStorage.setItem("galaxy-theme", mode);
  },
  init: function () {
    var saved = localStorage.getItem("galaxy-theme");
    if (saved === "dark") document.documentElement.classList.add("dark");
    document.querySelectorAll("[data-toggle-theme]").forEach(function (btn) {
      btn.onclick = function (e) { e.preventDefault(); galaxy.theme.toggle(); };
    });
  }
};

// ── Command Palette (Ctrl+K) ──
galaxy.initCommandPalette = function () {
  var palette = document.getElementById("cmd-palette");
  var input = document.getElementById("cmd-input");
  var results = document.getElementById("cmd-results");
  var trigger = document.getElementById("cmd-trigger");
  if (!palette || !input || !results) return;

  var pages = [
    { label: "Dashboard", url: "/desk", icon: "📊", category: "Pages" },
    { label: "DocTypes", url: "/desk/doctypes", icon: "📋", category: "Pages" },
    { label: "New DocType", url: "/desk/builder/doctype/new", icon: "🛠", category: "Pages" },
    { label: "Reports", url: "/desk/reports", icon: "📈", category: "Pages" },
    { label: "Server Scripts", url: "/desk/scripts", icon: "⚡", category: "Pages" },
    { label: "Bench Manager", url: "/desk/bench", icon: "⚙️", category: "Pages" },
    { label: "Tenants", url: "/desk/tenants", icon: "🏢", category: "Pages" },
    { label: "UI Guide", url: "/desk/ui-guide", icon: "🎨", category: "Pages" },
    { label: "Toggle Theme", action: "theme", icon: "🌓", category: "Actions" },
  ];

  function openPalette() {
    palette.style.display = "flex";
    input.value = "";
    results.innerHTML = renderResults(pages);
    setTimeout(function () { input.focus(); }, 50);
  }

  function closePalette() {
    palette.style.display = "none";
  }

  function renderResults(items) {
    if (!items.length) return '<div class="cmd-empty">No results found</div>';
    var cats = {};
    items.forEach(function (i) {
      if (!cats[i.category]) cats[i.category] = [];
      cats[i.category].push(i);
    });
    var html = "";
    Object.keys(cats).forEach(function (cat) {
      html += '<div class="cmd-category">' + cat + '</div>';
      cats[cat].forEach(function (i) {
        html += '<div class="cmd-item" data-url="' + (i.url || "") + '" data-action="' + (i.action || "") + '">' +
          '<span class="cmd-item-icon">' + (i.icon || "") + '</span>' +
          '<span class="cmd-item-label">' + i.label + '</span>' +
        '</div>';
      });
    });
    return html;
  }

  function filterItems(query) {
    if (!query) return pages;
    var q = query.toLowerCase();
    return pages.filter(function (i) {
      return i.label.toLowerCase().indexOf(q) !== -1;
    });
  }

  // Keyboard shortcut
  document.addEventListener("keydown", function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key === "k") {
      e.preventDefault();
      openPalette();
    }
    if (e.key === "Escape" && palette.style.display === "flex") {
      closePalette();
    }
  });

  // Trigger button
  if (trigger) trigger.onclick = function (e) { e.preventDefault(); openPalette(); };

  // Search filter
  input.addEventListener("input", function () {
    results.innerHTML = renderResults(filterItems(input.value));
  });

  // Item click
  results.addEventListener("click", function (e) {
    var item = e.target.closest(".cmd-item");
    if (!item) return;
    var url = item.dataset.url;
    var action = item.dataset.action;
    if (action === "theme") { galaxy.theme.toggle(); closePalette(); }
    else if (url) { window.location.href = url; }
  });

  // Keyboard navigation inside palette
  input.addEventListener("keydown", function (e) {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      var items = results.querySelectorAll(".cmd-item");
      var first = items[0];
      if (first) first.focus();
    }
  });

  // Allow item keyboard nav
  results.addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
      var focused = results.querySelector(".cmd-item:focus");
      if (focused) focused.click();
    }
  });

  // Close on backdrop click
  palette.addEventListener("click", function (e) {
    if (e.target === palette) closePalette();
  });
};

// ── User Menu ──
galaxy.initUserMenu = function () {
  var btn = document.getElementById("user-menu-btn");
  var menu = document.getElementById("user-dropdown");
  if (!btn || !menu) return;
  btn.onclick = function (e) {
    e.stopPropagation();
    menu.style.display = menu.style.display === "none" ? "block" : "none";
  };
  document.addEventListener("click", function () { menu.style.display = "none"; });
  menu.addEventListener("click", function (e) { e.stopPropagation(); });
};

// ── Sidebar ──
galaxy.initSidebar = function () {
  var toggle = document.getElementById("sidebar-toggle");
  var sidebar = document.getElementById("sidebar");
  var mobileToggle = document.getElementById("mobile-menu-toggle");
  if (toggle && sidebar) {
    toggle.onclick = function () {
      sidebar.classList.toggle("sidebar-collapsed");
      localStorage.setItem("galaxy-sidebar", sidebar.classList.contains("sidebar-collapsed") ? "collapsed" : "expanded");
    };
    var saved = localStorage.getItem("galaxy-sidebar");
    if (saved === "collapsed") sidebar.classList.add("sidebar-collapsed");
  }
  if (mobileToggle) {
    mobileToggle.onclick = function () {
      document.body.classList.toggle("mobile-nav-open");
    };
  }
};

// ── HTMX init ──
galaxy.initHTMX = function () {
  // If HTMX is loaded, set up CSRF
  if (typeof htmx !== "undefined") {
    htmx.on("htmx:configRequest", function (e) {
      if (csrfToken) {
        e.detail.headers["X-CSRF-Token"] = csrfToken;
      }
    });
    htmx.on("htmx:afterSwap", function (e) {
      galaxy.initNavActive();
      galaxy.codeEditor.init();
    });
    htmx.on("htmx:beforeRequest", function (e) {
      var indicator = e.detail.target && e.detail.target.querySelector(".htmx-indicator");
      if (indicator) indicator.style.opacity = "1";
    });
    htmx.on("htmx:afterRequest", function (e) {
      var indicator = e.detail.target && e.detail.target.querySelector(".htmx-indicator");
      if (indicator) indicator.style.opacity = "0";
    });
  }
};

// ── Bulk Actions ──
galaxy.selectedRecords = {};
galaxy.toggleAll = function (checkbox, doctype) {
  document.querySelectorAll(".galaxy-row-check").forEach(function (cb) {
    cb.checked = checkbox.checked;
    if (checkbox.checked) galaxy.selectedRecords[cb.value] = true;
    else delete galaxy.selectedRecords[cb.value];
  });
  galaxy.updateBulkBtn();
};
galaxy.onRowCheck = function () {
  var all = document.querySelectorAll(".galaxy-row-check");
  var checked = document.querySelectorAll(".galaxy-row-check:checked");
  var selectAll = document.querySelector(".galaxy-table-check input[type=checkbox]");
  if (selectAll) selectAll.checked = all.length === checked.length;
  checked.forEach(function (cb) { galaxy.selectedRecords[cb.value] = true; });
  document.querySelectorAll(".galaxy-row-check:not(:checked)").forEach(function (cb) { delete galaxy.selectedRecords[cb.value]; });
  galaxy.updateBulkBtn();
};
galaxy.updateBulkBtn = function () {
  var btn = document.getElementById("bulk-action-btn");
  if (!btn) return;
  var count = Object.keys(galaxy.selectedRecords).length;
  btn.style.display = count ? "inline-flex" : "none";
  btn.textContent = count + " selected ▼";
};
galaxy.bulkActions = function (doctype) {
  var ids = Object.keys(galaxy.selectedRecords);
  if (!ids.length) return;
  galaxy.confirm("Delete " + ids.length + " records?", { tone: "danger", confirmText: "Delete All" }).then(function (ok) {
    if (!ok) return;
    var promises = ids.map(function (id) {
      return fetch("/api/resource/" + doctype + "/" + id, { method: "DELETE" });
    });
    Promise.all(promises).then(function () {
      galaxy.toast("Deleted " + ids.length + " records", { tone: "success" });
      galaxy.selectedRecords = {};
      window.location.reload();
    });
  });
};

// ── Form Save ──
galaxy.saveForm = async function (doctype, name) {
  var data = {}, btn = document.querySelector(".form-actions-bar .galaxy-btn-primary") || document.querySelector(".page-actions .galaxy-btn-primary");
  if (btn) { btn.disabled = true; btn.textContent = "Saving..."; }
  document.querySelectorAll(".form-card-body [name]").forEach(function (el) {
    if (el.type === "checkbox") data[el.name] = el.checked;
    else data[el.name] = el.value;
  });
  try {
    var url = "/api/resource/" + doctype + (name ? "/" + name : "");
    var method = name ? "PUT" : "POST";
    var resp = await fetch(url, { method: method, headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) });
    var result = await resp.json();
    if (resp.ok && result.success) {
      galaxy.toast("Saved successfully", { tone: "success" });
      if (!name && result.data && result.data.name) {
        setTimeout(function () { window.location.href = "/desk/resource/" + doctype + "/" + result.data.name; }, 500);
      }
    } else {
      galaxy.toast(result.error || "Save failed", { tone: "danger" });
      if (btn) { btn.disabled = false; btn.textContent = name ? "Save" : "Create"; }
    }
  } catch (e) {
    galaxy.toast("Network error", { tone: "danger" });
    if (btn) { btn.disabled = false; btn.textContent = name ? "Save" : "Create"; }
  }
};

// ── Nav Active State ──
galaxy.initNavActive = function () {
  var path = window.location.pathname;
  document.querySelectorAll("[data-nav]").forEach(function (a) {
    var href = a.getAttribute("href");
    if (!href) return;
    var isActive = href === path || (path.startsWith(href) && href !== "/desk");
    a.classList.toggle("active", isActive);
  });
};

// ── Code Editor ──
galaxy.codeEditor = {};

galaxy.codeEditor.init = function () {
  document.querySelectorAll("textarea.galaxy-code-editor, textarea[data-code-editor]").forEach(function (ta) {
    if (ta.dataset.codeInited) return;
    ta.dataset.codeInited = "1";
    galaxy.codeEditor._enhance(ta);
  });
};

galaxy.codeEditor._enhance = function (ta) {
  var wrapper = document.createElement("div");
  wrapper.className = "code-editor-wrapper";
  ta.parentNode.insertBefore(wrapper, ta);
  wrapper.appendChild(ta);

  var toolbar = document.createElement("div");
  toolbar.className = "code-editor-toolbar";
  wrapper.insertBefore(toolbar, ta);

  var findBtn = document.createElement("button");
  findBtn.type = "button";
  findBtn.className = "galaxy-btn galaxy-btn-ghost galaxy-btn-neutral galaxy-btn-xs";
  findBtn.textContent = "Find";
  findBtn.onclick = function () { galaxy.codeEditor._findReplace(ta, "find"); };
  toolbar.appendChild(findBtn);

  var replaceBtn = document.createElement("button");
  replaceBtn.type = "button";
  replaceBtn.className = "galaxy-btn galaxy-btn-ghost galaxy-btn-neutral galaxy-btn-xs";
  replaceBtn.textContent = "Replace";
  replaceBtn.onclick = function () { galaxy.codeEditor._findReplace(ta, "replace"); };
  toolbar.appendChild(replaceBtn);

  var expandBtn = document.createElement("button");
  expandBtn.type = "button";
  expandBtn.className = "galaxy-btn galaxy-btn-ghost galaxy-btn-neutral galaxy-btn-xs";
  expandBtn.textContent = "⛶ Expand";
  expandBtn.onclick = function () { galaxy.codeEditor._toggleExpand(ta, wrapper); };
  toolbar.appendChild(expandBtn);

  var autoHint = document.createElement("button");
  autoHint.type = "button";
  autoHint.className = "galaxy-btn galaxy-btn-ghost galaxy-btn-neutral galaxy-btn-xs";
  autoHint.textContent = "Hints";
  autoHint.onclick = function () { galaxy.codeEditor._showHints(ta); };
  toolbar.appendChild(autoHint);

  ta.addEventListener("keydown", function (e) {
    if (e.key === "Tab") {
      e.preventDefault();
      var start = ta.selectionStart, end = ta.selectionEnd;
      ta.value = ta.value.substring(0, start) + "  " + ta.value.substring(end);
      ta.selectionStart = ta.selectionEnd = start + 2;
    }
    if (e.key === "f" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      galaxy.codeEditor._findReplace(ta, "find");
    }
    if (e.key === "h" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      galaxy.codeEditor._findReplace(ta, "replace");
    }
  });

  ta.style.minHeight = "200px";
  ta.style.width = "100%";
  ta.style.fontFamily = "'Cascadia Code', 'Fira Code', 'Consolas', monospace";
  ta.style.fontSize = "13px";
  ta.style.lineHeight = "1.5";
  ta.style.tabSize = "2";
};

galaxy.codeEditor._findReplace = function (ta, mode) {
  var q = prompt(mode === "find" ? "Find:" : "Find:");
  if (!q) return;
  if (mode === "find") {
    var idx = ta.value.indexOf(q);
    if (idx >= 0) { ta.focus(); ta.selectionStart = idx; ta.selectionEnd = idx + q.length; }
    else { galaxy.toast("Not found", { tone: "warning" }); }
  } else {
    var r = prompt("Replace with:");
    if (r === null) return;
    ta.value = ta.value.split(q).join(r);
    galaxy.toast("Replaced all occurrences", { tone: "success" });
  }
};

galaxy.codeEditor._toggleExpand = function (ta, wrapper) {
  var isExpanded = wrapper.classList.toggle("code-editor-expanded");
  if (isExpanded) {
    ta.style.position = "fixed";
    ta.style.top = "10px";
    ta.style.left = "10px";
    ta.style.width = "calc(100vw - 40px)";
    ta.style.height = "calc(100vh - 80px)";
    ta.style.zIndex = "9999";
    ta.style.maxWidth = "none";
  } else {
    ta.style.position = "";
    ta.style.top = "";
    ta.style.left = "";
    ta.style.width = "100%";
    ta.style.height = "";
    ta.style.zIndex = "";
    ta.style.maxWidth = "";
  }
};

galaxy.codeEditor._showHints = function (ta) {
  var fields = ta.dataset.fields || "";
  if (!fields) {
    galaxy.toast("No field hints available. Add data-fields='field1,field2' to the textarea.", { tone: "info" });
    return;
  }
  var list = fields.split(",").map(function (f) { return f.trim(); }).filter(Boolean);
  var insert = "{{ doc." + list[0] + " }}";
  if (list.length > 1) {
    var msg = "Available fields:\n" + list.map(function (f, i) { return (i + 1) + ". {{ doc." + f + " }}"; }).join("\n");
    var choice = prompt(msg + "\n\nEnter field number to insert (or 0 for all):");
    if (choice === null) return;
    var n = parseInt(choice, 10);
    if (n > 0 && n <= list.length) { insert = "{{ doc." + list[n - 1] + " }}"; }
    else if (n === 0) { insert = list.map(function (f) { return "{{ doc." + f + " }}"; }).join("\n"); }
    else return;
  }
  var start = ta.selectionStart;
  ta.value = ta.value.substring(0, start) + insert + ta.value.substring(ta.selectionEnd);
  ta.selectionStart = ta.selectionEnd = start + insert.length;
  ta.focus();
};

// ── Init code editors on DOM ready ──
document.addEventListener("DOMContentLoaded", function () {
  galaxy.codeEditor.init();
});

// Re-init after HTMX swaps
document.addEventListener("htmx:afterSwap", function () {
  galaxy.codeEditor.init();
});
