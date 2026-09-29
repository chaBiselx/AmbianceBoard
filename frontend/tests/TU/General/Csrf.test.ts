import { describe, it, expect, afterEach } from 'vitest';
import Csrf from '../../../src/modules/General/Csrf';

describe('Csrf.getToken', () => {
    afterEach(() => {
        document.head.innerHTML = '';
    });

    it('should return the token when the meta tag is present', () => {
        const meta = document.createElement('meta');
        meta.setAttribute('name', 'csrf-token');
        meta.setAttribute('content', 'abc123');
        document.head.appendChild(meta);

        expect(Csrf.getToken()).toBe('abc123');
    });

    it('should return null when the meta tag is missing', () => {
        expect(Csrf.getToken()).toBeNull();
    });
});
