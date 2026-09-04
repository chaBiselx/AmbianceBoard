import Csrf from '@/modules/General/Csrf';
import { OrganizerButtonPlaylist } from '@/modules/OrganizerButtonPlaylist';
import ConsoleCustom from '@/modules/General/ConsoleCustom';
import ConsoleTesteur from '@/modules/General/ConsoleTesteur';
import { OrganizerDragAndDropZone } from './OrganizerDom';
import { CleanOrderHandler } from './PlaylistOrder';

export class OrganizerApiClient {
    public async insertSection(insertSection: number): Promise<boolean> {
        const response = await this.request('UPDATE', { insertSection });
        return response.ok;
    }

    public async request(method: string, body: object): Promise<Response> {
        return fetch(OrganizerDragAndDropZone.getUrlFromAnySection(), {
            method,
            headers: {
                'X-CSRFToken': Csrf.getToken()!,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(body)
        });
    }
}

export class SendBackendAction {
    private readonly apiClient = new OrganizerApiClient();

    public addMusic(playlist: OrganizerButtonPlaylist, newOrder: number, section: number): void {
        this.send('POST', { idPlaylist: playlist.playlist.id, newOrder, section }, section);
    }

    public removeMusic(playlist: OrganizerButtonPlaylist, section: number): void {
        this.send('DELETE', { idPlaylist: playlist.playlist.id, section });
    }

    public updateMusic(playlist: OrganizerButtonPlaylist, newOrder: number, section: number): void {
        this.send('UPDATE', { idPlaylist: playlist.playlist.id, newOrder, section }, section);
    }

    public async insertSection(insertSection: number): Promise<boolean> {
        try {
            return await this.apiClient.insertSection(insertSection);
        } catch (error) {
            ConsoleCustom.error(error);
            return false;
        }
    }

    private send(method: string, body: object, section?: number): void {
        ConsoleTesteur.info(`Fetch called with method: ${method}, body: ${JSON.stringify(body)}, section: ${section}`);
        this.apiClient.request(method, body)
            .then(() => new CleanOrderHandler().resetBadge())
            .catch(error => ConsoleCustom.error(error));
    }
}