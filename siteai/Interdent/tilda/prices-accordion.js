/* Interdent Clinic — Tilda T123 accordion. Works with the original details.price-group markup. */
(function () {
  "use strict";
  function initPrices() {
    var root = document.getElementById("it-prices-accordion");
    if (!root || root.dataset.accordionReady === "1") return;
    var panels = Array.prototype.slice.call(root.querySelectorAll("details.price-group"));
    if (!panels.length) return;
    root.dataset.accordionReady = "1";
    panels.forEach(function (panel) {
      panel.addEventListener("toggle", function () {
        if (!panel.open) return;
        panels.forEach(function (other) {
          if (other !== panel && other.open) other.open = false;
        });
      });
    });
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initPrices, {once:true});
  } else {
    initPrices();
  }
})();