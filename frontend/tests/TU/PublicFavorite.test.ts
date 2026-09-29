import { beforeEach, describe, expect, it, vi } from 'vitest';

const favoriteMocks = vi.hoisted(() => ({ csrf: vi.fn() }));

vi.mock('@/modules/General/Csrf', () => ({ default: { getToken: favoriteMocks.csrf } }));

describe('PublicFavorite page script', () => {
    beforeEach(() => {
        vi.resetModules();
        vi.clearAllMocks();
        favoriteMocks.csrf.mockReturnValue('csrf-token');
        document.body.innerHTML = '<input class="favorite-action" type="checkbox" data-url="/favorite">';
    });

    it('sends POST when favoriting and DELETE when unfavoriting', async () => {
        const fetchMock = vi.fn();
        vi.stubGlobal('fetch', fetchMock);
        await import('@/PublicFavorite');
        document.dispatchEvent(new Event('DOMContentLoaded'));
        const favorite = document.querySelector<HTMLInputElement>('.favorite-action')!;

        favorite.click();
        expect(favorite.checked).toBe(true);
        expect(fetchMock).toHaveBeenLastCalledWith('/favorite', expect.objectContaining({ method: 'POST' }));

        favorite.click();
        expect(favorite.checked).toBe(false);
        expect(fetchMock).toHaveBeenLastCalledWith('/favorite', expect.objectContaining({
            method: 'DELETE',
            headers: { 'X-CSRFToken': 'csrf-token' },
        }));
    });
});