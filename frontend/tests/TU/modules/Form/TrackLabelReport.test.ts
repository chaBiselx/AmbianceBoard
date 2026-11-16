import { beforeEach, describe, expect, it, vi } from 'vitest';
import { initializeTrackLabelReport, TrackLabelReportDependencies } from '@/modules/Form/TrackLabelReport';

describe('TrackLabelReport', () => {
    beforeEach(() => {
        document.body.innerHTML = `
            <div class="music">
                <span class="track-label" data-label-id="12" data-label="rain" data-confidence="0.82">rain</span>
                <span class="track-label" data-label-id="13" data-label="wind" data-confidence="0.64">wind</span>
                <button class="btn-report-track-labels" data-url="/playlist/playlist-1/track/3/report"
                    data-modal-title="Report labels" data-modal-description="Select incorrect labels"
                    data-modal-submit="Send" data-modal-cancel="Cancel" data-modal-empty="Select at least one"
                    data-modal-success="Report received" data-modal-error="Could not send"></button>
            </div>
            <div id="modal-body"></div>
        `;
    });

    function createDependencies(): TrackLabelReportDependencies {
        return {
            fetch: vi.fn(),
            getCsrfToken: vi.fn().mockReturnValue('csrf-token'),
            showModal: vi.fn(options => {
                document.getElementById('modal-body')!.innerHTML = options.body;
                options.callback?.();
            }),
            hideModal: vi.fn(),
            notify: vi.fn(),
        };
    }

    it('shows label choices and submits only the selected label IDs', async () => {
        const dependencies = createDependencies();
        vi.mocked(dependencies.fetch).mockResolvedValue({
            ok: true,
            json: async () => ({ success: true }),
        } as Response);
        initializeTrackLabelReport(dependencies);

        document.querySelector<HTMLButtonElement>('.btn-report-track-labels')!.click();
        expect(dependencies.showModal).toHaveBeenCalledWith(expect.objectContaining({ title: 'Report labels' }));
        expect(document.querySelectorAll('.track-label-report-form input[name="label_ids"]')).toHaveLength(2);

        document.querySelector<HTMLInputElement>('input[value="13"]')!.checked = true;
        document.querySelector<HTMLFormElement>('.track-label-report-form')!.dispatchEvent(
            new Event('submit', { bubbles: true, cancelable: true }),
        );

        await vi.waitFor(() => expect(dependencies.fetch).toHaveBeenCalledOnce());
        const [, request] = vi.mocked(dependencies.fetch).mock.calls[0];
        expect(request?.method).toBe('POST');
        expect(request?.headers).toMatchObject({ 'X-CSRFToken': 'csrf-token' });
        expect(new URLSearchParams(request?.body as string).getAll('label_ids')).toEqual(['13']);
        await vi.waitFor(() => expect(dependencies.hideModal).toHaveBeenCalledOnce());
        expect(dependencies.notify).toHaveBeenCalledWith('Report received', 'success');
    });

    it('requires a selection and keeps the modal open when the request fails', async () => {
        const dependencies = createDependencies();
        vi.mocked(dependencies.fetch).mockResolvedValue({
            ok: false,
            json: async () => ({ success: false }),
        } as Response);
        initializeTrackLabelReport(dependencies);
        document.querySelector<HTMLButtonElement>('.btn-report-track-labels')!.click();

        const form = document.querySelector<HTMLFormElement>('.track-label-report-form')!;
        form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
        expect(document.querySelector('.track-label-report-error')!.classList.contains('d-none')).toBe(false);
        expect(dependencies.fetch).not.toHaveBeenCalled();

        document.querySelector<HTMLInputElement>('input[value="12"]')!.checked = true;
        form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
        await vi.waitFor(() => expect(dependencies.notify).toHaveBeenCalledWith('Could not send', 'danger'));
        expect(dependencies.hideModal).not.toHaveBeenCalled();
    });
});