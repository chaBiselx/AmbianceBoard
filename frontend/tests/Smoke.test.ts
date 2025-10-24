import { describe, it, expect } from 'vitest';

describe('Smoke Test', () => {
    it('should confirm the test environment is working', () => {
        // Test de base pour s'assurer que l'environnement JSDOM est fonctionnel
        expect(typeof globalThis).toBe('object');
        expect(typeof document).toBe('object');

        const element = document.createElement('div');
        element.textContent = 'Hello World';
        document.body.appendChild(element);

        const retrievedElement = document.querySelector('div');
        expect(retrievedElement).not.toBeNull();
        expect(retrievedElement?.textContent).toBe('Hello World');
    });
});
