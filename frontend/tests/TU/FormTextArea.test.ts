import { beforeEach, describe, expect, it, vi } from 'vitest';

const editorMocks = vi.hoisted(() => ({ create: vi.fn(), initialize: vi.fn() }));

vi.mock('@/modules/RichTextEditor/RichTextFactory', () => ({
    default: { create: editorMocks.create.mockReturnValue({ initialize: editorMocks.initialize }) },
}));

describe('FormTextArea page script', () => {
    beforeEach(() => {
        vi.resetModules();
        vi.clearAllMocks();
        document.body.innerHTML = `
            <textarea class="editor-container"></textarea>
            <textarea class="editor-container" data-editor="advanced"></textarea>
            <div class="editor-container"></div>
        `;
    });

    it('initializes textarea editors with their requested mode and skips other elements', async () => {
        await import('@/FormTextArea');
        document.dispatchEvent(new Event('DOMContentLoaded'));

        expect(editorMocks.create).toHaveBeenCalledTimes(2);
        expect(editorMocks.initialize).toHaveBeenNthCalledWith(1, 'simple');
        expect(editorMocks.initialize).toHaveBeenNthCalledWith(2, 'advanced');
    });
});