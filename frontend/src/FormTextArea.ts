import RichTextFactory from '@/modules/RichTextEditor/RichTextFactory';

document.addEventListener('DOMContentLoaded', () => {
    const listTextAreas = document.querySelectorAll('.editor-container');

    for (const textAreaElement of listTextAreas) {
        if (textAreaElement instanceof HTMLTextAreaElement === false) {
            continue;
        }
        const methode = textAreaElement.dataset.editor as 'simple' | 'advanced' || 'simple';
        RichTextFactory.create(textAreaElement).initialize(methode);
    }

     
});

