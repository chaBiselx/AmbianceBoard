import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import ShareLinkManager from '@/modules/Event/ShareLinkManager';

const shareMocks = vi.hoisted(() => ({
    notify: vi.fn(),
    warn: vi.fn(),
}));

vi.mock('@/modules/General/Notifications', () => ({
    default: { createClientNotification: shareMocks.notify },
}));

vi.mock('@/modules/General/ConsoleCustom', () => ({
    default: { warn: shareMocks.warn },
}));

describe('ShareLinkManager', () => {
    const writeText = vi.fn();

    beforeEach(() => {
        vi.clearAllMocks();
        vi.stubGlobal('navigator', { clipboard: { writeText } });
    });

    afterEach(() => {
        vi.unstubAllGlobals();
    });

    it('copies the data URL and reports success', async () => {
        writeText.mockResolvedValue(undefined);
        document.body.innerHTML = '<button class="share-link-btn" data-url="https://example.test/share"></button>';
        new ShareLinkManager().addEvent();

        document.querySelector<HTMLButtonElement>('.share-link-btn')!.click();

        await vi.waitFor(() => {
            expect(writeText).toHaveBeenCalledWith('https://example.test/share');
            expect(shareMocks.notify).toHaveBeenCalledWith({
                message: 'Lien copié dans le presse-papiers',
                type: 'success',
            });
        });
    });

    it('uses the href when no data URL exists', async () => {
        writeText.mockResolvedValue(undefined);
        document.body.innerHTML = '<a class="share-link-btn" href="https://example.test/href">Share</a>';
        new ShareLinkManager().addEvent();

        document.querySelector<HTMLAnchorElement>('.share-link-btn')!.click();

        await vi.waitFor(() => expect(writeText).toHaveBeenCalledWith('https://example.test/href'));
    });

    it('reports an error when the button has no URL', () => {
        document.body.innerHTML = '<button class="share-link-btn"></button>';
        new ShareLinkManager().addEvent();

        document.querySelector<HTMLButtonElement>('.share-link-btn')!.click();

        expect(shareMocks.notify).toHaveBeenCalledWith({ message: 'URL non trouvée', type: 'error' });
        expect(writeText).not.toHaveBeenCalled();
    });

    it('retries clipboard writes after a failure and reports a fallback failure', async () => {
        writeText.mockRejectedValueOnce(new Error('unavailable')).mockRejectedValueOnce(new Error('blocked'));
        document.body.innerHTML = '<button class="share-link-btn" data-url="https://example.test/share"></button>';
        new ShareLinkManager().addEvent();

        document.querySelector<HTMLButtonElement>('.share-link-btn')!.click();

        await vi.waitFor(() => {
            expect(writeText).toHaveBeenCalledTimes(2);
            expect(shareMocks.warn).toHaveBeenCalledOnce();
            expect(shareMocks.notify).toHaveBeenCalledWith({
                message: 'Impossible de copier le lien',
                type: 'error',
            });
        });
    });
});