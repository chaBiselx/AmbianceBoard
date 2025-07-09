import ModalCustom from '@/modules/General/Modal';
import Csrf from "@/modules/General/Csrf";


class ReportingContent {
    element: HTMLButtonElement | null = null;
    url: string | null = null

    constructor(idBtn: string) {
        const element = document.getElementById(idBtn)
        if (element) {
            this.element = element as HTMLButtonElement;
            if (this.element.dataset.url) this.url = this.element.dataset.url
        }
    }

    public addEvent() {
        if (this.element && this.url) {
            this.element.addEventListener('click', this.getElementsToReport.bind(this));
        }
    }

    private getElementsToReport() {
        const body = this.processCopyPastReportable();
        this.showModal("Reporting content", body)
    }

    private processCopyPastReportable(): string {
        let divGeneral = document.createElement('div');

        let sectionSelectElement = document.createElement('section');
        sectionSelectElement.id = "report-selector";
        sectionSelectElement.appendChild(this.generateSelector());
        divGeneral.appendChild(sectionSelectElement);

        let sectionForm = document.createElement('section');
        sectionForm.id = "report-section-form";
        sectionForm.classList.add("d-none")
        divGeneral.appendChild(sectionForm);



        return divGeneral.outerHTML
    }

    private generateSelector(): HTMLElement {
        let selectElement = document.createElement('div');
        selectElement.classList.add('flex-container');
        const reportableElements = document.querySelectorAll('.reportable')
        reportableElements.forEach(element => {
            let clonedElement = element.cloneNode(true) as HTMLElement;
            clonedElement.querySelectorAll('.reportable-ignore').forEach(el => {
                el.remove();
            })

            clonedElement.classList.add('event-report');
            selectElement.appendChild(clonedElement);
        });
        return selectElement

    }

    private showModal(title: string, body: string) {
        ModalCustom.show({
            title: title,
            body: body,
            footer: "",
            width: "xl",
            callback: () => {
                const reportableElements = document.querySelectorAll('.event-report')
                reportableElements.forEach(element => {
                    element.addEventListener('click', this.handleClickForm.bind(this));
                });
            }
        })

    }

    private handleClickForm(event: Event) {
        event.preventDefault();
        const elementClicked = event.target as HTMLElement;
        try {
            const reportManager = new ReportManager(elementClicked, this.url as string);
            const reportForm = reportManager.getReportForm();

            const form = document.getElementById('report-section-form') as HTMLElement;
            form.innerHTML = reportForm.generationForm();
            form.classList.remove('d-none');

            const sectionSelector = document.getElementById('report-selector') as HTMLElement;
            sectionSelector.classList.add('d-none');



        } catch (error) {
            console.error(error);
        }
    }
}

class ReportManager {
    HTMLElement: HTMLElement
    url: string | null = null
    constructor(HTMLElement: HTMLElement, url: string) {
        this.HTMLElement = HTMLElement
        this.url = url
    }

    getReportForm(): ReportFormElement {
        if (!this.url) throw new Error('Url not found');

        if (this.HTMLElement.classList.contains('playlist-element')) {
            return new ReportFormPlaylist(this.HTMLElement, this.url)
        } else if (this.HTMLElement.classList.contains('soundboard-element')) {
            return new ReportFormSoundboard(this.HTMLElement, this.url)
        }
        throw new Error('Element non reportable');
    }
}

interface ReportFormElement {
    HTMLElement: HTMLElement
    generationForm(): string
    addHidden(): string
    addSelectorForm(): string
    addSpecifiqueForm(): string
    addValidation(): string
}

class ReportFormBase implements ReportFormElement {
    HTMLElement: HTMLElement
    urlForm: string
    constructor(el: HTMLElement, urlForm: string) {
        this.HTMLElement = el
        this.urlForm = urlForm
    }

    generationForm(): string {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = this.urlForm;
        form.innerHTML =
            this.addCsrf() +
            this.addRedirectLink() +
            this.addHidden() +
            this.addSelectorForm() +
            this.addDefaultForm() +
            this.addSpecifiqueForm() +
            this.addValidation();

        return form.outerHTML
    }

    addCsrf(): string {
        const csrfToken = Csrf.getToken()!
        return `<input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">`
    }

    addRedirectLink(): string {
        return `<input type="hidden" name="redirect" value="${window.location.href}">`
    }

    addHidden(): string {
        throw new Error('Method not implemented.');
    }

    addSelectorForm(): string {
        throw new Error('Method not implemented.');
    }

    addSpecifiqueForm(): string {
        throw new Error('Method not implemented.');
    }

    addValidation(): string {
        return this.addFormGroup(`<button type="submit" class="btn btn-primary float-end">Signaler</button>`);
    }

    public addDefaultForm(): string {
        return this.addUserCommentaire()
    }

    public addFormGroup(content: string) {
        const div = document.createElement('div');
        div.classList.add('form-group');
        div.innerHTML = content;
        return div.outerHTML
    }

    private addUserCommentaire(): string {
        return this.addFormGroup(`<label for="element-description">Description</label>
        <textarea class="form-control" name="element-description" id="element-description" rows="3"></textarea>`)
    }
}

class ReportFormPlaylist extends ReportFormBase implements ReportFormElement {

    addHidden(): string {
        return this.addFormGroup(`
        <input type="hidden" name="element-type" id="element-type" value="playlist">
        <input type="hidden" name="element-id" id="element-id" value="${this.HTMLElement.dataset.id}">`)
    }
    addSelectorForm(): string {
        return this.addFormGroup(`<label for="element-precision">Element à signaler</label>
        <select class="form-control" name="element-precision" id="element-precision">
          <option value="">Choisir</option>
          <option value="image">Image</option>
          <option value="text">Texte</option>
          <option value="music">Musique</option>
          <option value="copyright">Copyright</option>
        </select>`)
    }

    addSpecifiqueForm(): string {
        return '';
    }


}

class ReportFormSoundboard extends ReportFormBase implements ReportFormElement {

    addHidden(): string {
        return this.addFormGroup(`
        <input type="hidden" name="element-type" id="element-type" value="soundboard">
        <input type="hidden" name="element-id" id="element-id" value="${this.HTMLElement.dataset.id}">`)
    }

    addSelectorForm(): string {
        return this.addFormGroup(`<label for="element-precision">Element à signaler</label>
        <select class="form-control" name="element-precision" id="element-precision">
          <option value="">Choisir</option>
          <option value="image">Image</option>
          <option value="text">Texte</option>
        </select>`)
    }

    addSpecifiqueForm(): string {
        return '';
    }
}


export default ReportingContent;

