
document.addEventListener("DOMContentLoaded", () => {
    const passwordRules = new PasswordRules('id_password')
    passwordRules.addEvent()
});



class PasswordRules {
    IdPasswordInput: string
    
    constructor(el: string) {
        this.IdPasswordInput = el
    }

    public addEvent() {
        const passwordInput = this.getPasswordInput()
        passwordInput.addEventListener('input', this.validatePassword.bind(this))
    }

    public getPasswordInput() : HTMLInputElement {
        return document.getElementById(this.IdPasswordInput) as HTMLInputElement
    }

    private validatePassword() {
        const passwordInput = this.getPasswordInput();
        const password = passwordInput.value;

        const rules = {
            minLength: password.length >= 8,
            hasUpperCase: /[A-Z]/.test(password),
            hasLowerCase: /[a-z]/.test(password),
            hasNumber: /\d/.test(password),
            hasSpecialChar: /[!@#€£$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(password)
        };
    
        // Vérification de toutes les règles
        const validation = {
            isValid: Object.values(rules).every(rule => rule === true),
        };
    
        // Création des messages d'erreur si nécessaire
        const passwordRules = document.getElementsByClassName('password-rules');
        for (const rule of passwordRules) {
            const ruleId = rule.id.split('_')[2];
            if (rules[ruleId as keyof typeof rules]) {
                rule.classList.add('text-success');
                rule.classList.remove('text-danger');
            } else {
                rule.classList.add('text-danger');
                rule.classList.remove('text-success');
            }
        }
    
        return validation;
    }
}