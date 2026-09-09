import BaseAudioAdapter from '@/modules/Audio/BaseAudioAdapter';

class HtmlAudioAdapter extends BaseAudioAdapter {
    constructor(audioElement: HTMLAudioElement) {
        super(audioElement);
    }

    play(): Promise<void> {
        return this.audioElement.play();
    }
}

export default HtmlAudioAdapter;
