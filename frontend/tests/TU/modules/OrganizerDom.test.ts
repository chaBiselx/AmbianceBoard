import { beforeEach, describe, expect, it } from 'vitest';
import { OrganizerDragAndDropZone, SectionConfig } from '@/modules/SoundboardOrganizer/OrganizerDom';

describe('OrganizerDragAndDropZone', () => {
    beforeEach(() => {
        document.body.innerHTML = '';
    });

    it('gets the update URL from the organizer container when no section exists', () => {
        document.body.innerHTML = '<div id="associated-playlists-container" data-url="/soundboard/update"></div>';

        expect(OrganizerDragAndDropZone.getUrlFromAnySection()).toBe('/soundboard/update');
    });

    it('gets the update URL when a section exists', () => {
        document.body.innerHTML = `
            <div id="associated-playlists-container" data-url="/soundboard/update">
                <div id="associated-playlists-section-1"></div>
            </div>
        `;

        expect(OrganizerDragAndDropZone.getUrlFromAnySection()).toBe('/soundboard/update');
    });

    it('uses section number 1 as the next number when no sections exist', () => {
        SectionConfig.refreshMaxSections();

        expect(SectionConfig.getMaxSections()).toBe(0);
        expect(SectionConfig.getNextSectionNumber()).toBe(1);
    });
});
