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
