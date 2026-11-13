import { beforeEach, describe, expect, it } from 'vitest';
import Sidebar from '../../../src/modules/General/Sidebar';

describe('Sidebar', () => {
    beforeEach(() => {
        document.body.innerHTML = '<button class="navbar-toggler"></button><div class="sidebar"></div>';
    });

    it('toggles the sidebar when its mobile button is clicked', () => {
        new Sidebar().addEvent();
        const button = document.querySelector('.navbar-toggler')!;
        const sidebar = document.querySelector('.sidebar')!;

        button.dispatchEvent(new Event('click'));
        expect(sidebar.classList.contains('d-block')).toBe(true);
        button.dispatchEvent(new Event('click'));
        expect(sidebar.classList.contains('d-block')).toBe(false);
    });
});
