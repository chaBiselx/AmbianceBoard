import Csrf from '@/modules/General/Csrf';
import Time from '@/modules/Util/Time';

class UserActivityLog {
    url: string | null = null;
    element: HTMLElement | null = null;

    constructor() {
        this.element = document.getElementById('trace_user_activity') || null;
    }

    private getUrl() {
        return this.element?.dataset.url || null;
    }

    public addEvent() {
        if (this.element) {
            window.addEventListener('beforeunload', () => {
                this.postActivityLog(true);
            });

            setInterval(() => {
                this.postActivityLog();
            }, Time.get_minutes(15));
        }
    }

    private postActivityLog(keepalive = false) {
        const url = this.getUrl();
        if (url) {
            fetch(url, {
                method: 'POST',
                keepalive,
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': Csrf.getToken()!
                },
            })
                .then(_response => {
                    // Log envoyé avec succès
                })
                .catch(error => {
                    console.error('There was a problem with the fetch operation:', error);
                });
        }
    }
}

export default UserActivityLog;
