document.addEventListener("DOMContentLoaded", function () {
  // Auto-dismiss flash alerts
  document.querySelectorAll(".alert").forEach(function (el) {
    setTimeout(function () {
      const alert = bootstrap.Alert.getOrCreateInstance(el);
      if (alert) alert.close();
    }, 4500);
  });

  // Delete confirmation for any form with data-confirm-delete
  document.querySelectorAll("form[data-confirm-delete]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      if (!confirm(form.dataset.confirmDelete || "Are you sure you want to delete this?")) {
        e.preventDefault();
      }
    });
  });
});

// ---------- PWA "Download App" button ----------
// The browser fires beforeinstallprompt only when the site meets install
// criteria (manifest + service worker + HTTPS). We capture that event and
// reveal our own button, instead of relying on users to find the browser's
// own menu option.
let deferredInstallPrompt = null;

window.addEventListener("beforeinstallprompt", function (e) {
  e.preventDefault();
  deferredInstallPrompt = e;
  document.querySelectorAll("#installAppBtn").forEach(function (btn) {
    btn.classList.remove("d-none");
  });
});

document.addEventListener("click", function (e) {
  const btn = e.target.closest("#installAppBtn");
  if (!btn || !deferredInstallPrompt) return;
  deferredInstallPrompt.prompt();
  deferredInstallPrompt.userChoice.finally(function () {
    deferredInstallPrompt = null;
    document.querySelectorAll("#installAppBtn").forEach(function (b) {
      b.classList.add("d-none");
    });
  });
});

// Already installed and running standalone? Hide the button — nothing to
// install. (iOS Safari has no beforeinstallprompt at all; those users still
// use Share -> Add to Home Screen, which we can't trigger programmatically.)
window.addEventListener("appinstalled", function () {
  document.querySelectorAll("#installAppBtn").forEach(function (btn) {
    btn.classList.add("d-none");
  });
});
