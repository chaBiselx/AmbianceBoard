/**
 * Why: le premier clic audio peut etre plus lent a cause de l'etablissement reseau
 * (resolution DNS + handshake TCP/TLS) vers l'endpoint de streaming.
 *
 * How: on lit les data-playlist-uri presentes dans le DOM pour extraire les origines,
 * puis on injecte des <link rel="dns-prefetch"> et <link rel="preconnect">.
 * Cela n'envoie pas de requete audio et ne change pas la logique metier de lecture.
 */
class StreamConnectionWarmup {
    private readonly PRECONNECT_REL = 'preconnect';
    private readonly DNS_PREFETCH_REL = 'dns-prefetch';

    public initialize(): void {
        const origins = this.collectPlaylistOrigins();
        for (const origin of origins) {
            this.addHint(this.DNS_PREFETCH_REL, origin);
            this.addHint(this.PRECONNECT_REL, origin);
        }
    }

    private collectPlaylistOrigins(): Set<string> {
        const origins = new Set<string>();
        const elements = document.querySelectorAll('.playlist-link');
        for (const element of elements) {
            if (!(element instanceof HTMLElement)) continue;
            const streamUrl = element.dataset.playlistUri;
            if (!streamUrl) continue;

            try {
                const origin = new URL(streamUrl, globalThis.location.origin).origin;
                origins.add(origin);
            } catch {
                // URL invalide: ignoree pour garder une initialisation robuste.
            }
        }
        return origins;
    }

    private addHint(rel: string, href: string): void {
        const selector = `link[rel="${rel}"][href="${href}"]`;
        if (document.head.querySelector(selector)) return;

        const link = document.createElement('link');
        link.rel = rel;
        link.href = href;
        document.head.appendChild(link);
    }
}

export default StreamConnectionWarmup;
