import Quill from 'quill';
import RicheTextInterface from './RicheTextInterface';

class RichTextQuills implements RicheTextInterface {
    private textArea: HTMLTextAreaElement;
    private quill: Quill|null = null;

    constructor(textArea: HTMLTextAreaElement) {
        this.textArea = textArea;
    }

    public initialize(type: 'simple' | 'advanced'): void {
        // Récupérer le texte par défaut du textarea

        //ajouter un div au meme niveau que le textarea pour y insérer quill
        const quillContainer = document.createElement('div');
        quillContainer.innerHTML = this.textArea.value;
        this.textArea.parentNode!.insertBefore(quillContainer, this.textArea.nextSibling);
        this.textArea.classList.add('d-none'); // Masquer le textarea d'origine
        quillContainer as HTMLElement;


        this.quill = new Quill(quillContainer, {
            modules: {
                toolbar: [
                    [{ header: [1, 2, 3, 4, 5, 6, false] }],
                    ['bold', 'italic', 'underline', 'strike'],
                    ['image', 'code-block'],
                    ['link'],
                    [{ 'script': 'sub' }, { 'script': 'super' }],
                    [{ 'list': 'ordered' }, { 'list': 'bullet' }],
                    ['clean']
                ],
            },
            placeholder: 'Créer votre texte',
            theme: 'snow', // or 'bubble'
        });

        this.quill.on('text-change', () =>{
                this.updateHtmlOutput()
        })
    }

    private updateHtmlOutput(): void {
        if(!this.quill) {
            return;
        }
        this.textArea.value = this.quill.root.innerHTML;
    }
}
export default RichTextQuills;