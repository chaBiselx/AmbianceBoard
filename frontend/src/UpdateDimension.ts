
import Cookie from "@/modules/Cookie";


document.addEventListener("DOMContentLoaded", () => {
    const listElement = document.getElementsByClassName('block-update') as HTMLCollectionOf<HTMLElement>;
    if (listElement) {
        for (const element of listElement) {
            const updateDim = new UpdateDimensionElement(element);
            updateDim.addEventListener();
        }
    }
});

class UpdateDimensionElement {
    minDimension: number = 50;
    maxDimension: number = 200;
    step: number = 25;
    element: HTMLElement
    url: string
    type: string
    classDimension: string
    demoElement: HTMLDivElement
    constructor(element: HTMLElement) {
        this.element = element
        this.url = element.dataset.url!
        this.type = element.dataset.type!
        this.demoElement = document.getElementById(`demo-${this.type}`) as HTMLDivElement;

        const regex = new RegExp(String.raw`${this.type}-dim-\d+`, "g");
        const match = regex.exec(this.demoElement.className);
        if (match?.[0]) {
            this.classDimension = match[0]
        } else {
            throw new Error("Aucune dimension trouvée");
        }
    }

    public addEventListener() {
        const increase = this.element.getElementsByClassName('btn-increase')[0] as HTMLButtonElement;
        const decrease = this.element.getElementsByClassName('btn-decrease')[0] as HTMLButtonElement;
        increase.addEventListener('click', this.increase.bind(this));
        decrease.addEventListener('click', this.decrease.bind(this));

    }

    private increase(event: Event) {
        event.preventDefault();
        this.updateDimension('increase');
    }

    private decrease(event: Event) {
        event.preventDefault();
        this.updateDimension('decrease');
    }

    private updateDimension(Type: string) {
        const dim = this.getNewDiemnsion(Type);
        const classDimensiontemp = this.type + '-dim-' + dim;
        if (classDimensiontemp !== this.classDimension) {
            this.demoElement.classList.add(classDimensiontemp);
            this.demoElement.classList.remove(this.classDimension);
            this.classDimension = classDimensiontemp
            this.updateBdd(dim);
        }
    }

    private updateBdd(dim: number) {
        fetch(this.url, {
            method: 'UPDATE',
            headers: {
                'X-CSRFToken': Cookie.get('csrftoken')!
            },
            body: JSON.stringify({ dim: dim })
        })
    }

    private getNewDiemnsion(Type: string): number {
        let actualDim = parseInt(this.classDimension.replace(this.type + '-dim-', ''));
        if (Type === 'increase') {
            return Math.min(this.maxDimension, actualDim + this.step);
        } else {
            return Math.max(this.minDimension, actualDim - this.step);
        }
    }

}
