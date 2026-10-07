import Notification from '@/modules/General/Notifications';



class PlayerCustomFactory {
    static create(root: ParentNode = document, onPlay?: (player: PlayerCustom) => void): PlayerCustom[] {
        const players: PlayerCustom[] = [];
        const listPlayer = root.querySelectorAll('.player-custom')
        for (const player of listPlayer) {
            const playerCust = new PlayerCustom(player as HTMLDivElement, onPlay)
            if (player.classList.contains('player-custom-small')) {
                playerCust.setTypePlayer('small');
            }
            playerCust.generate();
            players.push(playerCust);
        }
        return players;
    }
}

class PlayerCustom {
    divPlayer: HTMLDivElement
    audioPlayer: HTMLAudioElement
    url: string
    instanceLoaded: boolean = false
    private readonly listeners = new AbortController();
    private controls: HTMLDivElement | null = null;
    private playbackVersion = 0;
    private typePlayer: string = 'standard';

    constructor(player: HTMLDivElement, private readonly onPlay?: (player: PlayerCustom) => void) {
        this.divPlayer = player
        this.url = player.dataset.url!
        this.audioPlayer = player.getElementsByTagName('audio')[0]!
    }

    public generate() {
        if (this.controls || this.listeners.signal.aborted) return;
        this.generateHtmlPlayer()
    }

    public setTypePlayer(type: string) {
        this.typePlayer = type;
    }

    private generateHtmlPlayer() {
        let container = document.createElement("div");
        this.controls = container;
        container.classList.add("player-custom-container", "border", "border-primary", "rounded", "d-block");

        let divButton = document.createElement("div");
        divButton.classList.add("d-inline-block", "btn-group", "btn-group-player");

        const buttonStart = this.generateButtonPlayPause();
        divButton.appendChild(buttonStart);

        let buttonReload: HTMLButtonElement | null = null;
        if (this.typePlayer !== 'small') {
            buttonReload = this.generateButtonRestart();
            divButton.appendChild(buttonReload);
        }



        container.appendChild(divButton);

        const divCurrent = this.generateTimerBlock();
        container.appendChild(divCurrent);

        const divSeeker = this.generateSeekerBlock();
        container.appendChild(divSeeker);


        this.divPlayer.append(container)
        buttonStart.addEventListener('click', this.togglePlayer.bind(this), { signal: this.listeners.signal });
        if (buttonReload) {
            buttonReload.addEventListener('click', this.reload.bind(this), { signal: this.listeners.signal });
        }
        this.audioPlayer.addEventListener('ended', () => this.stop(true), { signal: this.listeners.signal });
        this.audioPlayer.addEventListener('error', () => this.handleError(), { signal: this.listeners.signal });
    }

    private generateButtonPlayPause() {
        let buttonStart = document.createElement("button");
        buttonStart.classList.add("btn", "btn-sm", "btn-primary", "btn-play");
        buttonStart.type = "button";
        buttonStart.title = this.divPlayer.dataset.playLabel || 'Play / pause';
        buttonStart.setAttribute('aria-label', buttonStart.title);
        const otherClass = this.generateotherClassBtn();
        buttonStart.innerHTML = "<i class=\"play-icon fa-solid fa-play " + otherClass + "\"></i><i class=\"pause-icon fa-solid fa-pause d-none " + otherClass + "\"></i>";
        return buttonStart
    }

    private generateButtonRestart() {
        let buttonReload = document.createElement("button");
        buttonReload.classList.add("btn", "btn-sm", "btn-secondary", "btn-reload");
        buttonReload.type = "button";
        buttonReload.title = this.divPlayer.dataset.restartLabel || 'Restart';
        buttonReload.setAttribute('aria-label', buttonReload.title);
        const otherClass = this.generateotherClassBtn();

        buttonReload.innerHTML = "<i class=\"fa-solid fa-arrows-rotate " + otherClass + "\"></i>";
        return buttonReload
    }

    private generateotherClassBtn(): string {
        let otherClass = "";
        if (this.typePlayer === 'small') {
            otherClass = "fa-xs";
        }
        return otherClass;
    }

    private generateTimerBlock() {
        let divCurrent = document.createElement("div");
        divCurrent.classList.add("timer", "d-none", "float-end", "mx-2");
        divCurrent.innerHTML = "<span class=\"current-time\">0:00</span> / <span class=\"duration\">0:00</span>";
        return divCurrent
    }

    private generateSeekerBlock() {
        let divSeeker = document.createElement("div");
        divSeeker.classList.add("seeker", "d-none", "mx-2");
        divSeeker.innerHTML = "<input disabled class=\"seeker-input form-range \" type=\"range\" min=\"0\" max=\"100\" value=\"0\" class=\"seeker-range\" step=\"1\"/>";
        divSeeker.querySelector('input')!.setAttribute('aria-label', this.divPlayer.dataset.seekLabel || 'Playback position');

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
        if (this.listeners.signal.aborted) return;
        this.onPlay?.(this);
        this.loadInstance();
        this.divPlayer.getElementsByClassName('play-icon')[0].classList.add('d-none');
        this.divPlayer.getElementsByClassName('pause-icon')[0].classList.remove('d-none');

        const version = ++this.playbackVersion;
        void this.audioPlayer.play()?.catch(() => {
            if (version === this.playbackVersion && !this.listeners.signal.aborted) this.handleError();
        });
    }

    private handleError(): void {
        this.stopPlayer();
        Notification.createClientNotification({
            message: "Erreur lors de la lecture de l'audio.",
            type: 'danger',
            duration: 2000,
        });
    }

    private loadInstance() {
        if (!this.instanceLoaded) {
            this.instanceLoaded = true;
            this.audioPlayer.src = this.url;
            this.audioPlayer.addEventListener('loadedmetadata', this.loadedmetadata.bind(this), { signal: this.listeners.signal });
            this.audioPlayer.addEventListener('timeupdate', this.updateTime.bind(this), { signal: this.listeners.signal });
            const seekerInput = this.getSeekerElement();
            seekerInput.removeAttribute('disabled')
            seekerInput.addEventListener('input', this.updateDuration.bind(this), { signal: this.listeners.signal });
            const seekerDiv = this.divPlayer.getElementsByClassName('seeker')[0] as HTMLDivElement;
            seekerDiv.classList.remove('d-none');
            seekerDiv.classList.add('d-block');
            const timerDiv = this.divPlayer.getElementsByClassName('timer')[0] as HTMLDivElement;
            timerDiv.classList.remove('d-none');
            timerDiv.classList.add('d-inline-block');

        }
    }

    private stopPlayer() {
        this.playbackVersion++;
        this.divPlayer.getElementsByClassName('pause-icon')[0].classList.add('d-none');
        this.divPlayer.getElementsByClassName('play-icon')[0].classList.remove('d-none');
        this.audioPlayer.pause();
    }

    public stop(reset = false): void {
        if (this.listeners.signal.aborted) return;
        this.stopPlayer();
        if (reset) {
            this.audioPlayer.currentTime = 0;
            this.divPlayer.getElementsByClassName('current-time')[0].textContent = '0:00';
            this.getSeekerElement().value = '0';
        }
    }

    public destroy(): void {
        if (this.listeners.signal.aborted) return;
        this.stop(true);
        this.listeners.abort();
        this.audioPlayer.removeAttribute('src');
        if (this.instanceLoaded) this.audioPlayer.load();
        this.controls?.remove();
    }

    public reload() {
        if (this.listeners.signal.aborted) return;
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
        if (timeVal === Infinity) {
            return '∞'
        }
        let time = Math.floor(timeVal / 60);
        let secs = Math.floor(timeVal - time * 60);
        const secsString = (secs < 10 ? ":0" : ":") + secs;
        return time.toString() + secsString;
    }
}

export { PlayerCustomFactory, PlayerCustom };