import Config from '@/modules/General/Config'
class WakeLock {
    private wakeLock: WakeLockSentinel | null = null;

    constructor() {
        document.addEventListener("visibilitychange", this.handleVisibilityChange);
    }

    // Demande le Wake Lock pour l'écran
    public async start(): Promise<void> {
        try {
            this.wakeLock = await navigator.wakeLock.request("screen");
            if (Config.DEBUG) console.log("Wake Lock activé !");

            // Gérer la libération du Wake Lock
            this.wakeLock.addEventListener("release", () => {
                if (Config.DEBUG) console.log("Wake Lock relâché");
                this.wakeLock = null;
            });

        } catch (err) {
            if (Config.DEBUG) console.error(`Erreur avec Wake Lock: ${(err as Error).message}`);
        }
    }

    // Gestion de la visibilité de la page
    private readonly handleVisibilityChange = async (): Promise<void> => {
        if (this.wakeLock !== null && document.visibilityState === "visible") {
            this.start();
        }
    };

    // Libère le Wake Lock
    public stop(): void {
        if (this.wakeLock) {
            this.wakeLock.release();
            this.wakeLock = null;
        }
    }
}


export default WakeLock;