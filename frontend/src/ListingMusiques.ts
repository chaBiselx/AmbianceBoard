import Notification from '@/modules/General/Notifications';


document.addEventListener('DOMContentLoaded', () => {
    const listPlayer = document.getElementsByClassName('player-custom')
    for (const player of listPlayer) {
        const playerCust = new PlayerCustom(player as HTMLDivElement)
        playerCust.generate();
    }
});

class PlayerCustom {
    divPlayer: HTMLDivElement
    audioPlayer: HTMLAudioElement
    url: string
    instanceLoaded: boolean = false
    constructor(player: HTMLDivElement) {
        this.divPlayer = player
        this.url = player.dataset.url!
        this.audioPlayer = player.getElementsByTagName('audio')[0]!
    }

    public generate() {
        this.generateHtmlPlayer()
    }

    private generateHtmlPlayer() {
        let container = document.createElement("div");
        container.classList.add("player-custom-container");
        container.classList.add("border");
        container.classList.add("border-primary");
        container.classList.add("rounded");
        container.classList.add("d-block");

        let divButton = document.createElement("div");
        divButton.classList.add("d-inline-block");
        divButton.classList.add("btn-group");
        divButton.classList.add("btn-group-player");

        const buttonStart = this.generateButtonPlayPause();
        divButton.appendChild(buttonStart);

        const buttonReload = this.generateButtonRestart();
        divButton.appendChild(buttonReload);

        container.appendChild(divButton);

        const divCurrent = this.generateTimerBlock();
        container.appendChild(divCurrent);

        const divSeeker = this.generateSeekerBlock();
        container.appendChild(divSeeker);


        this.divPlayer.append(container)
        buttonStart.addEventListener('click', this.togglePlayer.bind(this));
        buttonReload.addEventListener('click', this.reload.bind(this));
    }

    private generateButtonPlayPause() {
        let buttonStart = document.createElement("button");
        buttonStart.classList.add("btn");
        buttonStart.classList.add("btn-sm");
        buttonStart.classList.add("btn-primary");
        buttonStart.classList.add("btn-play");
        buttonStart.type = "button";
        buttonStart.innerHTML = "<i class=\"play-icon fa-solid fa-play\"></i><i class=\"pause-icon fa-solid fa-pause d-none\"></i>";
        return buttonStart
    }

    private generateButtonRestart() {
        let buttonReload = document.createElement("button");
        buttonReload.classList.add("btn");
        buttonReload.classList.add("btn-sm");
        buttonReload.classList.add("btn-secondary");
        buttonReload.classList.add("btn-reload");
        buttonReload.type = "button";
        buttonReload.innerHTML = "<i class=\"fa-solid fa-arrows-rotate\"></i>";
        return buttonReload
    }

    private generateTimerBlock() {
        let divCurrent = document.createElement("div");
        divCurrent.classList.add("timer");
        divCurrent.classList.add("d-none");
        divCurrent.classList.add("float-end");
        divCurrent.classList.add("mx-2");
        divCurrent.innerHTML = "<span class=\"current-time\">0:00</span> / <span class=\"duration\">0:00</span>";
        return divCurrent
    }

    private generateSeekerBlock() {
        let divSeeker = document.createElement("div");
        divSeeker.classList.add("seeker");
        divSeeker.classList.add("d-none");
        divSeeker.classList.add("mx-2");
        divSeeker.innerHTML = "<input disabled class=\"seeker-input form-range \" type=\"range\" min=\"0\" max=\"100\" value=\"0\" class=\"seeker-range\" step=\"1\"/>";

        return divSeeker;

    }

    public togglePlayer() {
        if (this.audioPlayer.paused) {
            this.startPlayer();
        } else {
            this.stopPlayer();
        }
    }

    private startPlayer() {
        this.loadInstance();
        this.divPlayer.getElementsByClassName('play-icon')[0].classList.add('d-none');
        this.divPlayer.getElementsByClassName('pause-icon')[0].classList.remove('d-none');

        this.audioPlayer.addEventListener('error', (e) => {
            Notification.createClientNotification({
                message: "Erreur lors de la lecture de l'audio.",
                type: 'danger',
                duration: 2000,
            });
        });

        this.audioPlayer.play();
    }

    private loadInstance() {
        if (!this.instanceLoaded) {
            this.instanceLoaded = true;
            this.audioPlayer.src = this.url;
            this.audioPlayer.addEventListener('loadedmetadata', this.loadedmetadata.bind(this));
            this.audioPlayer.addEventListener('timeupdate', this.updateTime.bind(this));
            const seekerInput = this.getSeekerElement();
            seekerInput.removeAttribute('disabled')
            seekerInput.addEventListener('input', this.updateDuration.bind(this));
            const seekerDiv = this.divPlayer.getElementsByClassName('seeker')[0] as HTMLDivElement;
            seekerDiv.classList.remove('d-none');
            seekerDiv.classList.add('d-block');
            const timerDiv = this.divPlayer.getElementsByClassName('timer')[0] as HTMLDivElement;
            timerDiv.classList.remove('d-none');
            timerDiv.classList.add('d-inline-block');

        }
    }

    private stopPlayer() {
        this.divPlayer.getElementsByClassName('pause-icon')[0].classList.add('d-none');
        this.divPlayer.getElementsByClassName('play-icon')[0].classList.remove('d-none');
        this.audioPlayer.pause();
    }

    public reload() {
        this.stopPlayer();
        this.audioPlayer.currentTime = 0;
        this.startPlayer();
    }

    private loadedmetadata() {
        this.divPlayer.getElementsByClassName('duration')[0].innerHTML = this.audioTimeFormat(this.audioPlayer.duration)
    }

    private updateDuration() {

        const seekerInput = this.getSeekerElement();
        this.audioPlayer.currentTime = this.audioPlayer.duration * (seekerInput.valueAsNumber / 100)


    }

    private getSeekerElement() {
        return this.divPlayer.getElementsByClassName('seeker-input')[0] as HTMLInputElement
    }

    private updateTime() {
        this.divPlayer.getElementsByClassName('current-time')[0].innerHTML = this.audioTimeFormat(this.audioPlayer.currentTime)
        this.seekerUpdateTime()
    }

    private seekerUpdateTime() {
        let nt = this.audioPlayer.currentTime * (100 / this.audioPlayer.duration);
        const seekerInput = this.getSeekerElement();
        seekerInput.value = nt.toString();
    }


    private audioTimeFormat(timeVal: number): string {
        if(timeVal === Infinity){
            return '∞'
        }
        let time = Math.floor(timeVal / 60);
        let secs = Math.floor(timeVal - time * 60);
        const secsString = (secs < 10 ? ":0" : ":") + secs;
        return time.toString() + secsString;
    }
}
