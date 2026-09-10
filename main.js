/**
 * main.js
 * -------
 * Small progressive-enhancement helpers shared across pages:
 *  - Show/hide password toggle buttons
 *  - Auto-dismiss flash messages after a few seconds
 */

document.addEventListener("DOMContentLoaded", function () {
    // --- Password visibility toggles ---------------------------------------
    document.querySelectorAll(".toggle-visibility").forEach((btn) => {
        btn.addEventListener("click", () => {
            const targetId = btn.getAttribute("data-target");
            const input = document.getElementById(targetId);
            if (!input) return;
            const isHidden = input.type === "password";
            input.type = isHidden ? "text" : "password";
            btn.textContent = isHidden ? "🙈" : "👁️";
        });
    });

    // --- Auto-dismiss flash messages ----------------------------------------
    document.querySelectorAll(".flash").forEach((flash) => {
        setTimeout(() => {
            flash.style.transition = "opacity 0.4s ease";
            flash.style.opacity = "0";
            setTimeout(() => flash.remove(), 400);
        }, 6000);
    });
});
