(function () {
  const form = document.getElementById("expenseForm");
  if (!form) return;

  const fields = ["mode", "km", "other_amount", "cng_bus_amount",
                   "courier_transport_amount", "food_amount", "fuel_type"];
  const totalDisplay = document.getElementById("totalPreview");
  const kmRateNote = document.getElementById("kmRateNote");
  const modeSelect = document.getElementById("modeSelect");
  const fuelTypeWrap = document.getElementById("fuelTypeWrap");

  let timer = null;

  function toggleFuelType() {
    if (!modeSelect || !fuelTypeWrap) return;
    fuelTypeWrap.style.display = modeSelect.value === "Car" ? "block" : "none";
  }

  function recalc() {
    clearTimeout(timer);
    timer = setTimeout(function () {
      const params = new URLSearchParams();
      fields.forEach(function (f) {
        const el = form.elements[f];
        params.append(f, el ? el.value : "");
      });

      fetch("/api/calculate-total?" + params.toString())
        .then((r) => r.json())
        .then((data) => {
          totalDisplay.textContent = "₹" + Number(data.total_amount).toFixed(2);
          if (data.km_rate > 0) {
            kmRateNote.textContent = "KM rate applied: ₹" + data.km_rate + "/km  →  ₹" + data.km_amount.toFixed(2);
            kmRateNote.style.display = "block";
          } else {
            kmRateNote.style.display = "none";
          }
        })
        .catch(() => {});
    }, 200);
  }

  fields.forEach(function (f) {
    const el = form.elements[f];
    if (el) el.addEventListener("input", recalc);
    if (el) el.addEventListener("change", recalc);
  });

  if (modeSelect) {
    modeSelect.addEventListener("change", function () {
      toggleFuelType();
      recalc();
    });
  }

  toggleFuelType();
  recalc();
})();
