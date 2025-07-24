import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { PaginationManager } from '@/modules/PaginationManager';

describe('PaginationManager', () => {
    // On prépare le DOM avant chaque test
    beforeEach(() => {
        document.body.innerHTML = `
            <ul id="pagination">
                <li class="page-item"><button class="page-link" data-page="1">1</button></li>
                <li class="page-item"><button class="page-link" data-page="2">2</button></li>
                <li class="page-item disabled"><button class="page-link" data-page="3">3</button></li>
            </ul>
        `;
        
        // On simule window.location pour les tests
        const url = new URL('http://localhost:3000');
        // @ts-ignore
        delete window.location;
        window.location = { ...window.location, href: url.href, replace: vi.fn() };
    });

    // On nettoie les mocks après chaque test
    afterEach(() => {
        vi.restoreAllMocks();
    });

    it('should return the correct parameter name', () => {
        expect(PaginationManager.getParameterName()).toBe('page');
    });

    it('should add event listeners and change page on click', () => {
        const paginationManager = new PaginationManager();
        paginationManager.addEventListeners();

        const page2Button = document.querySelector('[data-page="2"]') as HTMLButtonElement;
        page2Button.click();

        // On vérifie que la fonction de remplacement d'URL a été appelée
        expect(window.location.replace).toHaveBeenCalledTimes(1);
        // On vérifie qu'elle a été appelée avec la bonne URL
        expect(window.location.replace).toHaveBeenCalledWith('http://localhost:3000/?page=2');
    });

    it('should not change page when a disabled button is clicked', () => {
        const paginationManager = new PaginationManager();
        paginationManager.addEventListeners();

        const page3Button = document.querySelector('[data-page="3"]') as HTMLButtonElement;
        page3Button.click();

        // La fonction de remplacement d'URL ne doit pas avoir été appelée
        expect(window.location.replace).not.toHaveBeenCalled();
    });

    it('should not throw an error if pagination element does not exist', () => {
        // On vide le body pour ce test spécifique
        document.body.innerHTML = ''; 
        
        const paginationManager = new PaginationManager();
        
        // On s'attend à ce que l'appel ne lève aucune exception
        expect(() => paginationManager.addEventListeners()).not.toThrow();
    });
});
