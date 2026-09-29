import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import GeneralTheme from '../../../src/modules/General/GeneralTheme';
import Cookie from '../../../src/modules/General/Cookie';
import Csrf from '../../../src/modules/General/Csrf';
import Boolean from '../../../src/modules/Util/Boolean';

vi.mock('@/modules/General/Cookie', () => ({
    default: { get: vi.fn(), set: vi.fn() },
}));
vi.mock('@/modules/General/Csrf', () => ({
    default: { getToken: vi.fn() },
}));
vi.mock('@/modules/Util/Boolean', () => ({
    default: { convert: vi.fn() },
}));

function setupButton(dataset: Record<string, string> = {}) {
    document.body.innerHTML = '';
    const button = document.createElement('button');
    button.id = 'darkModeToggle';
    Object.entries(dataset).forEach(([key, value]) => {
        button.dataset[key] = value;
    });
    document.body.appendChild(button);
    return button;
}

describe('GeneralTheme', () => {
    beforeEach(() => {
        document.documentElement.removeAttribute('data-bs-theme');
        vi.mocked(Cookie.get).mockReturnValue(null);
        vi.mocked(Boolean.convert).mockReturnValue(false);
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    it('should use the cookie theme when there is no backend preference', () => {
        setupButton();
        vi.mocked(Cookie.get).mockReturnValue('dark');

        const theme = new GeneralTheme();

        expect(theme.theme).toBe('dark');
        expect(document.documentElement.dataset.bsTheme).toBe('dark');
    });

    it('should fall back to light when there is no cookie', () => {
        setupButton();

        const theme = new GeneralTheme();

        expect(theme.theme).toBe('light');
    });

    it('should use the html attribute as backend preference and persist it to the cookie', () => {
        setupButton({ backendSaved: 'true' });
        vi.mocked(Boolean.convert).mockReturnValue(true);
        document.documentElement.dataset.bsTheme = 'dark';

        const theme = new GeneralTheme();

        expect(theme.theme).toBe('dark');
        expect(Cookie.set).toHaveBeenCalledWith('theme', 'dark');
    });

    it('should fall back to light when the backend preference has no html attribute', () => {
        setupButton({ backendSaved: 'true' });
        vi.mocked(Boolean.convert).mockReturnValue(true);

        const theme = new GeneralTheme();

        expect(theme.theme).toBe('light');
    });

    it('should toggle the theme, icon and persist it when the button is clicked', () => {
        setupButton({ url: '/save-theme' });
        vi.mocked(Csrf.getToken).mockReturnValue('csrf-token');
        globalThis.fetch = vi.fn().mockResolvedValue({ json: () => Promise.resolve({}) });

        const theme = new GeneralTheme();
        theme.addEvent();
        expect(theme.buttonToggle.innerHTML).toContain('fa-moon');

        theme.buttonToggle.dispatchEvent(new Event('click'));

        expect(theme.theme).toBe('dark');
        expect(theme.buttonToggle.innerHTML).toContain('fa-sun');
        expect(document.documentElement.dataset.bsTheme).toBe('dark');
        expect(Cookie.set).toHaveBeenCalledWith('theme', 'dark');
        expect(globalThis.fetch).toHaveBeenCalledWith('/save-theme', expect.objectContaining({ method: 'UPDATE' }));

        theme.buttonToggle.dispatchEvent(new Event('click'));

        expect(theme.theme).toBe('light');
        expect(theme.buttonToggle.innerHTML).toContain('fa-moon');
    });

    it('should not save the theme to the server when the url is missing', () => {
        setupButton();
        vi.mocked(Csrf.getToken).mockReturnValue('csrf-token');
        globalThis.fetch = vi.fn();

        const theme = new GeneralTheme();
        theme.addEvent();
        theme.buttonToggle.dispatchEvent(new Event('click'));

        expect(globalThis.fetch).not.toHaveBeenCalled();
    });

    it('should not save the theme to the server when the csrf token is missing', () => {
        setupButton({ url: '/save-theme' });
        vi.mocked(Csrf.getToken).mockReturnValue(null);
        globalThis.fetch = vi.fn();

        const theme = new GeneralTheme();
        theme.addEvent();
        theme.buttonToggle.dispatchEvent(new Event('click'));

        expect(globalThis.fetch).not.toHaveBeenCalled();
    });

    it('should log the error when the save request fails', async () => {
        setupButton({ url: '/save-theme' });
        vi.mocked(Csrf.getToken).mockReturnValue('csrf-token');
        const error = new Error('network error');
        globalThis.fetch = vi.fn().mockRejectedValue(error);
        const errorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

        const theme = new GeneralTheme();
        theme.addEvent();
        theme.buttonToggle.dispatchEvent(new Event('click'));
        await new Promise((resolve) => setTimeout(resolve, 0));

        expect(errorSpy).toHaveBeenCalledWith(error);
    });

    it('should do nothing when addEvent is called without a button', () => {
        setupButton();
        const theme = new GeneralTheme();
        // @ts-ignore simulate a missing button
        theme.buttonToggle = null;
        expect(() => theme.addEvent()).not.toThrow();
    });
});
