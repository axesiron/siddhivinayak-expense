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
// criteria (manifest + service worker + HTTPS). We capture that event so
// the button can trigger it directly. If that event never fires (iOS
// Safari never fires it at all; Chrome may not fire it immediately on a
// fresh visit), clicking the button falls back to clear manual steps
// instead of silently doing nothing.
let deferredInstallPrompt = null;

window.addEventListener("beforeinstallprompt", function (e) {
  e.preventDefault();
  deferredInstallPrompt = e;
});

window.addEventListener("appinstalled", function () {
  deferredInstallPrompt = null;
});

function showInstallInstructions() {
  const body = document.getElementById("installInstructionsBody");
  const modalEl = document.getElementById("installInstructionsModal");
  if (!body || !modalEl) return;

  const ua = navigator.userAgent || "";
  const isIOS = /iPad|iPhone|iPod/.test(ua);
  const isAndroid = /Android/.test(ua);
  const isSafari = /Safari/.test(ua) && !/Chrome/.test(ua);

  let html;
  if (isIOS && isSafari) {
    html = "Tap the <strong>Share</strong> icon (square with an arrow) at the bottom of Safari, " +
           "then scroll down and tap <strong>\"Add to Home Screen\"</strong>.";
  } else if (isAndroid) {
    html = "Tap the <strong>&#8942;</strong> (three dots) menu at the top right of Chrome, " +
           "then tap <strong>\"Install app\"</strong> or <strong>\"Add to Home screen\"</strong>.";
  } else {
    html = "Look for an install icon in your browser's address bar, or open the browser menu " +
           "and choose <strong>\"Install app\"</strong> (Chrome/Edge) or " +
           "<strong>\"Add to Home Screen\"</strong>.";
  }
  body.innerHTML = "<p>" + html + "</p>";

  const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
  modal.show();
}

document.addEventListener("click", function (e) {
  const btn = e.target.closest("#installAppBtn");
  if (!btn) return;

  if (deferredInstallPrompt) {
    deferredInstallPrompt.prompt();
    deferredInstallPrompt.userChoice.finally(function () {
      deferredInstallPrompt = null;
    });
  } else {
    showInstallInstructions();
  }
});
