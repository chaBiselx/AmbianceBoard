import ConsoleCustom from "./modules/General/ConsoleCustom";
import ModalCustom from '@/modules/General/Modal';


document.addEventListener('DOMContentLoaded', () => {
    new CronExecuter().addEvent();
})

class CronExecuter {

    addEvent() {
        for (const el of document.querySelectorAll('.cron-execute-button')) {
            el.addEventListener('click', this.executeCron.bind(this));
        }
    }

    private async executeCron(event: Event) {
        const target = event.target as HTMLElement;
        const cronUrl = target.dataset.url;
        const cronTitle = target.dataset.title;
        if (cronUrl && cronTitle) {
            ModalCustom.wait();

            fetch(cronUrl, {
                method: 'GET',
            })
                .then(response => response.text())
                .then((body) => {
                    ModalCustom.show({
                        title: cronTitle,
                        body: body,
                        footer: "",
                        width: "lg",
                    })


                })
                .catch(error => {
                    ConsoleCustom.error('Erreur lors de la requête AJAX:', error);
                    ModalCustom.show({
                        title: "Erreur",
                        body: "Une erreur est survenue lors de l'exécution du cron.<br><br>Détail : " + (error?.message || error),
                        footer: "",
                        width: "md",
                    });
                });
        
        }
    }
}
