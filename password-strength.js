/**
 * password-strength.js
 * ---------------------
 * Real-time password strength meter for the registration form.
 *
 * IMPORTANT: this is a UX aid only. The server re-validates every
 * password with the exact same rules in utils/validators.py, because
 * client-side JavaScript can always be disabled or bypassed by an
 * attacker submitting the form directly.
 */

(function () {
    const passwordInput = document.getElementById("password");
    const confirmInput = document.getElementById("confirm_password");
    if (!passwordInput) return; // Not on this page

    const fill = document.getElementById("strength-fill");
    const label = document.getElementById("strength-label");
    const matchHint = document.getElementById("match-hint");

    const rules = {
        length: { el: document.getElementById("rule-length"), test: (p) => p.length >= 8 },
        upper: { el: document.getElementById("rule-upper"), test: (p) => /[A-Z]/.test(p) },
        lower: { el: document.getElementById("rule-lower"), test: (p) => /[a-z]/.test(p) },
        digit: { el: document.getElementById("rule-digit"), test: (p) => /\d/.test(p) },
        special: { el: document.getElementById("rule-special"), test: (p) => /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>/?]/.test(p) },
    };

    const levels = [
        { max: 1, color: "#E5566B", text: "Very weak" },
        { max: 2, color: "#E5566B", text: "Weak" },
        { max: 3, color: "#E8A73D", text: "Fair" },
        { max: 4, color: "#45C7D8", text: "Good" },
        { max: 5, color: "#4FCB8D", text: "Strong" },
    ];

    function evaluate(password) {
        let score = 0;
        Object.values(rules).forEach(({ el, test }) => {
            const passed = test(password);
            if (passed) score += 1;
            if (el) el.classList.toggle("met", passed);
        });

        // Small bonus for length beyond the minimum — rewards longer passphrases.
        if (password.length >= 12) score = Math.min(score + 0.5, 5);

        return score;
    }

    function render(password) {
        if (!password) {
            fill.style.width = "0%";
            fill.style.backgroundColor = "#E5566B";
            label.textContent = "Enter a password";
            return;
        }

        const score = evaluate(password);
        const level = levels.find((l) => score <= l.max) || levels[levels.length - 1];
        const pct = Math.min((score / 5) * 100, 100);

        fill.style.width = pct + "%";
        fill.style.backgroundColor = level.color;
        label.textContent = level.text;
    }

    function renderMatch() {
        if (!confirmInput || !matchHint) return;
        if (!confirmInput.value) {
            matchHint.textContent = "";
            matchHint.className = "hint";
            return;
        }
        const matches = passwordInput.value === confirmInput.value;
        matchHint.textContent = matches ? "Passwords match" : "Passwords do not match";
        matchHint.className = "hint " + (matches ? "valid" : "invalid");
    }

    passwordInput.addEventListener("input", (e) => {
        render(e.target.value);
        renderMatch();
    });

    if (confirmInput) {
        confirmInput.addEventListener("input", renderMatch);
    }
})();
