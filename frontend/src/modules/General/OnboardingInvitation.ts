import Notification from '@/modules/General/Notifications';
import Time from "@/modules/Util/Time";
import translate from '@/modules/Util/Translation';

type InvitationState = {
    startedAt: number;
    prompted: boolean;
    dismissed: boolean;
};

export default class OnboardingInvitation {
    private readonly storageKey = 'ambiance_onboarding_invitation';
    private readonly delay: number;
    private readonly state: InvitationState | null = null;
    private timer: ReturnType<typeof setTimeout> | null = null;
    private notification: { close: () => void } | null = null;
    private onStart: (() => void) | null = null;
    private readonly onPageHide = () => this.pause();
    private readonly onPageShow = () => this.schedule();

    constructor(delayInSeconds: number = 10) {
        this.delay = Time.get_seconds(delayInSeconds);
        console.log('Saved onboarding invitation constructor:');
        
        const now = Date.now();
        this.state = { startedAt: now, prompted: false, dismissed: false };
        try {
            const saved: unknown = JSON.parse(localStorage.getItem(this.storageKey) ?? 'null');
            console.log('Saved onboarding invitation state:', saved);
    
            if (saved && typeof saved === 'object' && 'startedAt' in saved && 'prompted' in saved
                && typeof saved.startedAt === 'number' && Number.isFinite(saved.startedAt)
                && saved.startedAt >= 0 && saved.startedAt <= now && typeof saved.prompted === 'boolean') {
                this.state = {
                    startedAt: saved.startedAt,
                    prompted: saved.prompted,
                    dismissed: 'dismissed' in saved && saved.dismissed === true,
                };
            }
        } catch {
            this.state = { startedAt: now, prompted: false, dismissed: false };
        }
        this.saveState();
    }

    public initialize(onStart: () => void): void {
        if (!this.state || this.state.dismissed || this.onStart ) return;

        this.onStart = onStart;
        globalThis.addEventListener('pagehide', this.onPageHide);
        globalThis.addEventListener('pageshow', this.onPageShow);
        this.schedule();
    }

    public suppress(): void {
        if (this.state) {
            this.state.prompted = true;
            this.state.dismissed = true;
            this.saveState();
        }
        this.dispose();
    }

    public dispose(): void {
        this.pause();
        globalThis.removeEventListener('pagehide', this.onPageHide);
        globalThis.removeEventListener('pageshow', this.onPageShow);
        this.onStart = null;
    }

    private schedule(): void {
        if (!this.state || this.hasBeenDismissed() || !this.onStart || this.timer !== null || this.notification) return;

        const remaining = Math.max(0, this.delay - (Date.now() - this.state.startedAt));
        this.timer = setTimeout(() => {
            this.timer = null;
            if (!this.state || this.hasBeenDismissed() || !this.onStart || this.notification) return;

            this.state.prompted = true;
            this.saveState();
            const onStart = this.onStart;
            this.notification = Notification.createActionNotification({
                title: translate('onboarding.invitation.title'),
                message: translate('onboarding.invitation.message'),
                actionLabel: translate('onboarding.invitation.action'),
                dismissLabel: translate('onboarding.invitation.dismiss'),
                type: 'warning',
                onAction: () => {
                    this.suppress();
                    onStart();
                },
                onDismiss: () => this.suppress(),
            });
        }, remaining);
    }

    private pause(): void {
        if (this.timer !== null) {
            clearTimeout(this.timer);
            this.timer = null;
        }
        this.notification?.close();
        this.notification = null;
    }

    private saveState(): void {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(this.state));
        } catch {
            return;
        }
    }

    private hasBeenDismissed(): boolean {
        if (this.state?.dismissed) return true;
        try {
            return JSON.parse(localStorage.getItem(this.storageKey) ?? 'null')?.dismissed === true;
        } catch {
            return false;
        }
    }
}