/**
 * Empêche de relancer un script avant l'expiration du délai minimal défini
 * côté serveur (SOUNDBOARD_SCRIPT_COOLDOWN_MS).
 */
class ScriptCooldownGuard {
    private readonly lastStart = new Map<string, number>();

    constructor(private readonly cooldownMs: number) { }

    canStart(scriptUuid: string): boolean {
        if (this.cooldownMs <= 0) return true;
        const last = this.lastStart.get(scriptUuid);
        if (last === undefined) return true;
        return Date.now() - last >= this.cooldownMs;
    }

    markStart(scriptUuid: string, button: HTMLButtonElement | null = null): void {
        this.lastStart.set(scriptUuid, Date.now());
        if (!button || this.cooldownMs <= 0) return;
        button.classList.add('script-cooldown');
        button.disabled = true;
        setTimeout(() => {
            button.classList.remove('script-cooldown');
            button.disabled = false;
        }, this.cooldownMs);
    }
}

export default ScriptCooldownGuard;
