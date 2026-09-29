import { beforeEach, describe, expect, it, vi } from 'vitest';
import ReportingContent from '@/modules/ReportingContent';

const reportMocks = vi.hoisted(() => ({
    show: vi.fn((options: { body: string; callback: () => void }) => {
        document.body.insertAdjacentHTML('beforeend', options.body);
    }),
    csrf: vi.fn(),
}));

vi.mock('@/modules/General/Modal', () => ({ default: { show: reportMocks.show } }));
vi.mock('@/modules/General/Csrf', () => ({ default: { getToken: reportMocks.csrf } }));

describe('ReportingContent', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        reportMocks.csrf.mockReturnValue('csrf-token');
        document.body.innerHTML = `
            <button id="reportButton" data-url="/report"></button>
            <div class="reportable playlist-element" data-id="playlist-12">
                <img src="/cover.png"><span class="private-copy">Not copied</span>
            </div>
        `;
    });

    it('builds a playlist report form from a selected reportable element', () => {
        new ReportingContent('reportButton').addEvent();
        document.getElementById('reportButton')!.click();

        expect(reportMocks.show).toHaveBeenCalledWith(expect.objectContaining({
            title: 'Reporting content',
            width: 'xl',
        }));
        const modalOptions = reportMocks.show.mock.calls[0][0] as { callback: () => void };
        modalOptions.callback();
        const reportableClone = document.querySelector<HTMLElement>('.event-report')!;
        expect(reportableClone.classList.contains('reportable')).toBe(false);
        expect(reportableClone.querySelector('img')).not.toBeNull();
        expect(reportableClone.querySelector('.private-copy')).toBeNull();
        reportableClone.click();

        const formSection = document.getElementById('report-section-form')!;
        expect(formSection.classList.contains('d-none')).toBe(false);
        expect(formSection.innerHTML).toContain('name="element-type" id="element-type" value="playlist"');
        expect(formSection.innerHTML).toContain('name="element-id" id="element-id" value="playlist-12"');
        expect(formSection.innerHTML).toContain('name="csrfmiddlewaretoken" value="csrf-token"');
        expect(formSection.innerHTML).toContain('name="element-description"');
        expect(formSection.innerHTML).toContain('<option value="copyright">Copyright</option>');
        expect(document.getElementById('report-selector')!.classList.contains('d-none')).toBe(true);
    });

    it('uses the soundboard report type and does not attach without a report URL', () => {
        document.body.innerHTML = `
            <button id="reportButton" data-url="/report"></button>
            <div class="reportable soundboard-element" data-id="board-8"></div>
        `;
        new ReportingContent('reportButton').addEvent();
        document.getElementById('reportButton')!.click();
        const modalOptions = reportMocks.show.mock.calls[0][0] as { callback: () => void };
        modalOptions.callback();
        document.querySelector<HTMLElement>('.event-report')!.click();

        expect(document.getElementById('report-section-form')!.innerHTML).toContain('value="soundboard"');
        expect(document.getElementById('report-section-form')!.innerHTML).not.toContain('value="music"');

        document.body.innerHTML = '<button id="reportButton"></button>';
        new ReportingContent('reportButton').addEvent();
        document.getElementById('reportButton')!.click();
        expect(reportMocks.show).toHaveBeenCalledOnce();
    });
});