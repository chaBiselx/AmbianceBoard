import { beforeEach, describe, expect, it, vi } from 'vitest';
import ProposePlaylistToSoundboard from '@/modules/SoundBoardEditor/ProposePlaylistToSoundboard';

const proposalMocks = vi.hoisted(() => ({
    csrf: vi.fn(),
    notify: vi.fn(),
    show: vi.fn((options: { body: string }) => document.body.insertAdjacentHTML('beforeend', options.body)),
}));

vi.mock('@/modules/General/Csrf', () => ({ default: { getToken: proposalMocks.csrf } }));
vi.mock('@/modules/General/Notifications', () => ({ default: { createClientNotification: proposalMocks.notify } }));
vi.mock('@/modules/General/Modal', () => ({ default: { show: proposalMocks.show } }));

const proposalMarkup = `
    <div id="pagination"><li class="page-item"><button class="page-link" data-page="2">2</button></li></div>
    <select name="genre" data-edit-mode-filter="true"><option value="">All</option><option value="ambient">Ambient</option></select>
    <button class="btn-propose-playlist" data-url-propose="/propose">Propose</button>
    <button class="btn-propose-playlist" data-url-propose="/propose-fail">Fail</button>
`;

describe('ProposePlaylistToSoundboard', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        proposalMocks.csrf.mockReturnValue('csrf-token');
        document.body.innerHTML = `
            <button id="btn-propose-playlist-to-soundboard" data-url-list="/proposals"></button>
            <button class="proposal-withdraw-btn" data-url="/status">Withdraw</button>
        `;
    });

    it('loads a filtered/paginated list and handles proposal and status failures', async () => {
        const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
            const url = String(input);
            if (url.startsWith('http') || url.startsWith('/proposals')) {
                return { text: async () => proposalMarkup } as Response;
            }
            if (url === '/propose') {
                return { ok: true, json: async () => ({ success: true, message: 'Sent' }) } as Response;
            }
            if (url === '/propose-fail') {
                return { ok: false, json: async () => ({ error: 'Not allowed' }) } as Response;
            }
            if (url === '/status') {
                return { ok: false, json: async () => ({ error: 'Cannot withdraw' }) } as Response;
            }
            throw new Error(`Unexpected ${init?.method} ${url}`);
        });
        vi.stubGlobal('fetch', fetchMock);
        const manager = new ProposePlaylistToSoundboard();
        manager.addEvent();
        document.getElementById('btn-propose-playlist-to-soundboard')!.click();
        const modalOptions = proposalMocks.show.mock.calls[0][0] as { callback: () => void };
        modalOptions.callback();

        await vi.waitFor(() => expect(document.querySelector('.btn-propose-playlist')).not.toBeNull());
        const filter = document.querySelector<HTMLSelectElement>('[data-edit-mode-filter="true"]')!;
        filter.innerHTML = '<option value="">All</option><option value="ambient">Ambient</option>';
        filter.value = 'ambient';
        filter.dispatchEvent(new Event('change'));
        await vi.waitFor(() => expect(fetchMock.mock.calls.some(([url]) =>
            new URL(String(url), globalThis.location.origin).search === '?page=1&genre=ambient'
        )).toBe(true));

        document.querySelector<HTMLButtonElement>('.page-link')!.click();
        await vi.waitFor(() => expect(fetchMock.mock.calls.some(([url]) =>
            new URL(String(url), globalThis.location.origin).search === '?page=2&genre=ambient'
        )).toBe(true));

        document.querySelector<HTMLButtonElement>('[data-url-propose="/propose"]')!.click();
        await vi.waitFor(() => expect(proposalMocks.notify).toHaveBeenCalledWith({ message: 'Sent', type: 'success' }));

        const failedProposal = document.querySelector<HTMLButtonElement>('[data-url-propose="/propose-fail"]')!;
        failedProposal.click();
        await vi.waitFor(() => expect(proposalMocks.notify).toHaveBeenCalledWith({ message: 'Not allowed', type: 'error' }));
        expect(failedProposal.disabled).toBe(false);

        const statusButton = document.querySelector<HTMLButtonElement>('.proposal-withdraw-btn')!;
        statusButton.click();
        await vi.waitFor(() => expect(proposalMocks.notify).toHaveBeenCalledWith({ message: 'Cannot withdraw', type: 'error' }));
        expect(statusButton.disabled).toBe(false);
    });
});