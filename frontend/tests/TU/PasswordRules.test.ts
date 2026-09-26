import { beforeEach, describe, expect, it, vi } from 'vitest';

describe('PasswordRules page script', () => {
    beforeEach(() => {
        vi.resetModules();
        document.body.innerHTML = `
            <input id="id_password">
            <span id="rule_password_minLength" class="password-rules"></span>
            <span id="rule_password_hasUpperCase" class="password-rules"></span>
            <span id="rule_password_hasLowerCase" class="password-rules"></span>
            <span id="rule_password_hasNumber" class="password-rules"></span>
            <span id="rule_password_hasSpecialChar" class="password-rules"></span>
        `;
    });

    it('marks each requirement and accepts a password meeting all rules', async () => {
        await import('@/PasswordRules');
        document.dispatchEvent(new Event('DOMContentLoaded'));
        const input = document.getElementById('id_password') as HTMLInputElement;
        input.value = 'weak';
        input.dispatchEvent(new Event('input'));

        expect(document.querySelectorAll('.password-rules.text-danger')).toHaveLength(4);
        expect(document.querySelectorAll('.password-rules.text-success')).toHaveLength(1);

        input.value = 'StrongPass1!';
        input.dispatchEvent(new Event('input'));

        expect(document.querySelectorAll('.password-rules.text-success')).toHaveLength(5);
        expect(document.querySelectorAll('.password-rules.text-danger')).toHaveLength(0);
    });

    it('tolerates a missing password input during initialization', async () => {
        document.body.innerHTML = '';
        await import('@/PasswordRules');

        expect(() => document.dispatchEvent(new Event('DOMContentLoaded'))).not.toThrow();
    });
});