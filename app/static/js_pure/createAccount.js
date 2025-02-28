
document.addEventListener("DOMContentLoaded", (event) => {
    document.getElementById('id_password').addEventListener('input', validatePassword)
});

function validatePassword(event) {
    const password = event.target.value;

    const rules = {
        minLength: password.length >= 8,
        hasUpperCase: /[A-Z]/.test(password),
        hasLowerCase: /[a-z]/.test(password),
        hasNumber: /[0-9]/.test(password),
        hasSpecialChar: /[!@#€£$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)
    };

    // Vérification de toutes les règles
    const validation = {
        isValid: Object.values(rules).every(rule => rule === true),
    };


    // Création des messages d'erreur si nécessaire
    const passwordRules = document.getElementsByClassName('password-rules');
    for (const rule of passwordRules) {
        const ruleId = rule.id.split('_')[2];
        if (rules[ruleId]) {
            rule.classList.add('text-success');
            rule.classList.remove('text-danger');
        } else {
            rule.classList.add('text-danger');
            rule.classList.remove('text-success');
        }
    }

    return validation;
}