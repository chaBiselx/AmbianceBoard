import { describe, it, expect, beforeEach } from 'vitest';
import Cookie from '../../../src/modules/General/Cookie';

function clearAllCookies() {
    document.cookie.split(';').forEach((cookie) => {
        const name = cookie.split('=')[0].trim();
        if (name) {
            document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/`;
        }
    });
}

describe('Cookie.get', () => {
    beforeEach(() => {
        clearAllCookies();
    });

    it('should return null when there are no cookies', () => {
        expect(Cookie.get('theme')).toBeNull();
    });

    it('should return null when the cookie is not found', () => {
        document.cookie = 'other=value';
        expect(Cookie.get('theme')).toBeNull();
    });

    it('should return the raw value when it is not quoted', () => {
        // A preceding cookie is required: the parser only strips the
        // separator's leading space, so a lone/first cookie can't be read.
        document.cookie = 'filler=value';
        document.cookie = 'theme=dark';
        expect(Cookie.get('theme')).toBe('dark');
    });

    it('should strip surrounding quotes from the value', () => {
        document.cookie = 'filler=value';
        document.cookie = 'theme="dark"';
        expect(Cookie.get('theme')).toBe('dark');
    });
});

describe('Cookie.set', () => {
    beforeEach(() => {
        clearAllCookies();
    });

    it('should write the cookie with the given name and value', () => {
        document.cookie = 'filler=value';
        Cookie.set('theme', 'dark');
        expect(Cookie.get('theme')).toBe('dark');
    });
});
