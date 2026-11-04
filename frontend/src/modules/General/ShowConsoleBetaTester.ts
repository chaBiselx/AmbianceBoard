import ConsoleTraceServeur from '@/modules/General/ConsoleTraceServeur';

class ShowConsoleBetaTester {
    buttonShow: HTMLButtonElement | null = null;
    consoleElement: HTMLElement | null = null;

    constructor() {
        this.buttonShow = document.getElementById('showLoggerBetaTest') as HTMLButtonElement;
        this.consoleElement = document.getElementById('betaTestConsole');
    }

    public addEvent() {
        if (this.buttonShow && this.consoleElement) {
            this.buttonShow.addEventListener('click', this.toggleConsole.bind(this));
        }
    }

    private toggleConsole() {
        if (this.consoleElement) {
            if (this.consoleElement.classList.contains('d-none')) {
                ConsoleTraceServeur.log('Set console beta tester visible');
            }
            this.consoleElement.classList.toggle('d-none');
        }
    }
}

export default ShowConsoleBetaTester;
