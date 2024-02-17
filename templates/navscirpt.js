// Manually initialize Bootstrap components
document.addEventListener("DOMContentLoaded", function () {
    var buttons = document.querySelectorAll('[data-bs-toggle="collapse"]');
    buttons.forEach(function (button) {
      button.addEventListener("click", function () {
        var target = document.querySelector(button.getAttribute("data-bs-target"));
        if (target.classList.contains("show")) {
          target.classList.remove("show");
        } else {
          target.classList.add("show");
        }
      });
    });
  });