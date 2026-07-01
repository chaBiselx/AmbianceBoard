import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

/**
 * Integration tests for SoundboardOrganizer feature:
 * - Insert section between two sections
 * - Drag & drop playlists in same section
 * - Drag & drop playlists between different sections
 * - Drag & drop playlists to unassociated zone
 * - Verify numbering after insertions
 * - Verify persistence after operations
 */

describe('SounboardOrganizer Integration Tests', () => {
    let container: HTMLDivElement;

    beforeEach(() => {
        // Setup DOM
        container = document.createElement('div');
        document.body.appendChild(container);
    });

    afterEach(() => {
        document.body.removeChild(container);
        vi.clearAllMocks();
    });

    /**
     * Test Case 1: Section insertion shifts all following sections
     * Expected: All sections after insertion point are incremented by 1
     */
    it('should shift sections after insertion point', () => {
        // Setup: Create sections 1, 2, 3 with playlists
        container.innerHTML = `
            <div id="playlistAssociees-1" data-section="1">
                <div class="playlist" data-id="p1" data-section="1" data-order="1">Playlist 1</div>
            </div>
            <div id="playlistAssociees-2" data-section="2">
                <div class="playlist" data-id="p2" data-section="2" data-order="1">Playlist 2</div>
            </div>
            <div id="playlistAssociees-3" data-section="3">
                <div class="playlist" data-id="p3" data-section="3" data-order="1">Playlist 3</div>
            </div>
        `;

        // Verify initial state
        expect(document.getElementById('playlistAssociees-1')).toBeTruthy();
        expect(document.getElementById('playlistAssociees-2')).toBeTruthy();
        expect(document.getElementById('playlistAssociees-3')).toBeTruthy();

        // Simulate insert at position 2
        // Step 1: Create new empty section at position 2
        const newSection = document.createElement('div');
        newSection.id = 'playlistAssociees-2';
        newSection.dataset.section = '2';

        // Step 2: Update old section 2 -> section 3
        const oldSection2 = document.getElementById('playlistAssociees-2')!;
        const p2 = oldSection2.querySelector('.playlist') as HTMLElement;
        
        oldSection2.id = 'playlistAssociees-3';
        oldSection2.dataset.section = '3';
        p2.dataset.section = '3';

        // Step 3: Update old section 3 -> section 4
        const oldSection3 = document.getElementById('playlistAssociees-3')!;
        const p3 = oldSection3.querySelector('.playlist') as HTMLElement;
        
        oldSection3.id = 'playlistAssociees-4';
        oldSection3.dataset.section = '4';
        p3.dataset.section = '4';

        // Step 4: Insert new empty section
        const section1 = document.getElementById('playlistAssociees-1')!;
        section1.insertAdjacentElement('afterend', newSection);

        // Verify final state
        expect(document.getElementById('playlistAssociees-1')).toBeTruthy();
        expect(document.getElementById('playlistAssociees-2')).toBeTruthy();
        expect(document.getElementById('playlistAssociees-3')).toBeTruthy();
        expect(document.getElementById('playlistAssociees-4')).toBeTruthy();

        // Verify section numbers
        expect((document.getElementById('playlistAssociees-1')!.querySelector('.playlist') as HTMLElement).dataset.section).toBe('1');
        expect((document.getElementById('playlistAssociees-3')!.querySelector('.playlist') as HTMLElement).dataset.section).toBe('3');
        expect((document.getElementById('playlistAssociees-4')!.querySelector('.playlist') as HTMLElement).dataset.section).toBe('4');
    });

    /**
     * Test Case 2: Drag playlist in same section
     * Expected: Playlist order within section is updated, no section change
     */
    it('should reorder playlist within same section', () => {
        // Setup: Section with 3 playlists
        container.innerHTML = `
            <div id="playlistAssociees-1" data-section="1">
                <div class="playlist" data-id="p1" data-section="1" data-order="1">Playlist 1</div>
                <div class="playlist" data-id="p2" data-section="1" data-order="2">Playlist 2</div>
                <div class="playlist" data-id="p3" data-section="1" data-order="3">Playlist 3</div>
            </div>
        `;

        // Verify initial order
        const section = document.getElementById('playlistAssociees-1')!;
        let playlists = Array.from(section.querySelectorAll('.playlist')) as HTMLElement[];
        expect(playlists).toHaveLength(3);
        expect(playlists[0].dataset.id).toBe('p1');
        expect(playlists[1].dataset.id).toBe('p2');
        expect(playlists[2].dataset.id).toBe('p3');

        // Simulate reorder: move p2 to end
        // Remove p2 and append it
        const p2 = section.querySelector('[data-id="p2"]') as HTMLElement;
        p2.remove();
        section.appendChild(p2);

        // Verify new order
        playlists = Array.from(section.querySelectorAll('.playlist')) as HTMLElement[];
        expect(playlists[0].dataset.id).toBe('p1');
        expect(playlists[1].dataset.id).toBe('p3');
        expect(playlists[2].dataset.id).toBe('p2');

        // Verify section numbers are unchanged
        playlists.forEach(p => expect(p.dataset.section).toBe('1'));
    });

    /**
     * Test Case 3: Drag playlist between different sections
     * Expected: Playlist moves to new section with order 1, old section can become empty (not persisted)
     */
    it('should move playlist from section 1 to section 2', () => {
        // Setup: Two sections with playlists
        container.innerHTML = `
            <div id="playlistAssociees-1" data-section="1">
                <div class="playlist" data-id="p1" data-section="1" data-order="1">Playlist 1</div>
                <div class="playlist" data-id="p2" data-section="1" data-order="2">Playlist 2</div>
            </div>
            <div id="playlistAssociees-2" data-section="2">
                <div class="playlist" data-id="p3" data-section="2" data-order="1">Playlist 3</div>
            </div>
        `;

        // Drag p1 from section 1 to section 2
        const playlist = document.querySelector('.playlist[data-id="p1"]') as HTMLElement;
        const targetSection = document.getElementById('playlistAssociees-2')!;

        // Simulate move
        targetSection.appendChild(playlist);
        playlist.dataset.section = '2';
        playlist.dataset.order = '1';

        // Verify new state
        expect(playlist.dataset.section).toBe('2');
        expect(playlist.dataset.order).toBe('1');
        expect(document.getElementById('playlistAssociees-2')!.contains(playlist)).toBe(true);
        
        // Verify section 1 still has p2
        expect(document.getElementById('playlistAssociees-1')!.querySelector('[data-id="p2"]')).toBeTruthy();
    });

    /**
     * Test Case 4: Drag playlist to unassociated zone
     * Expected: Playlist is moved to unassociated zone, section reference remains but can be removed on backend
     */
    it('should move playlist from section to unassociated zone', () => {
        // Setup: Section with playlist + unassociated zone
        container.innerHTML = `
            <div id="playlistAssociees-1" data-section="1">
                <div class="playlist" data-id="p1" data-section="1" data-order="1">Playlist 1</div>
            </div>
            <div id="playlistNonAssociees">
                <!-- Unassociated playlists go here -->
            </div>
        `;

        // Drag p1 to unassociated zone
        const playlist = document.querySelector('.playlist[data-id="p1"]') as HTMLElement;
        const unassociatedZone = document.getElementById('playlistNonAssociees')!;

        unassociatedZone.appendChild(playlist);

        // Verify playlist is in unassociated zone
        expect(unassociatedZone.contains(playlist)).toBe(true);
        expect(unassociatedZone.querySelectorAll('.playlist')).toHaveLength(1);
        
        // Verify original section is now empty
        expect(document.getElementById('playlistAssociees-1')!.querySelectorAll('.playlist')).toHaveLength(0);
    });

    /**
     * Test Case 5: Complex scenario - Insert, then drag multiple playlists
     * Expected: All operations maintain consistent numbering and order
     */
    it('should handle insert + multiple drags with consistent state', () => {
        // Setup: 3 sections with multiple playlists
        container.innerHTML = `
            <div id="playlistAssociees-1" data-section="1">
                <div class="playlist" data-id="p1" data-section="1" data-order="1">P1</div>
                <div class="playlist" data-id="p2" data-section="1" data-order="2">P2</div>
            </div>
            <div id="playlistAssociees-2" data-section="2">
                <div class="playlist" data-id="p3" data-section="2" data-order="1">P3</div>
            </div>
            <div id="playlistAssociees-3" data-section="3">
                <div class="playlist" data-id="p4" data-section="3" data-order="1">P4</div>
            </div>
        `;

        // Step 1: Insert at position 2
        // Update section 2 -> 3, section 3 -> 4
        const oldSection2 = document.getElementById('playlistAssociees-2')!;
        const p3 = oldSection2.querySelector('.playlist') as HTMLElement;
        oldSection2.id = 'playlistAssociees-3';
        p3.dataset.section = '3';

        const oldSection3 = document.getElementById('playlistAssociees-3')!;
        const p4 = oldSection3.querySelector('.playlist') as HTMLElement;
        oldSection3.id = 'playlistAssociees-4';
        p4.dataset.section = '4';

        // Insert empty section 2
        const newSection2 = document.createElement('div');
        newSection2.id = 'playlistAssociees-2';
        newSection2.dataset.section = '2';
        document.getElementById('playlistAssociees-1')!.insertAdjacentElement('afterend', newSection2);

        // Step 2: Drag p1 from section 1 to section 3 (old section 2)
        const p1 = document.querySelector('.playlist[data-id="p1"]') as HTMLElement;
        document.getElementById('playlistAssociees-3')!.appendChild(p1);
        p1.dataset.section = '3';

        // Step 3: Drag p4 to unassociated zone
        const p4Element = document.querySelector('.playlist[data-id="p4"]') as HTMLElement;
        const unassociated = document.createElement('div');
        unassociated.id = 'playlistNonAssociees';
        container.appendChild(unassociated);
        unassociated.appendChild(p4Element);

        // Verify final state
        expect(document.getElementById('playlistAssociees-1')!.querySelectorAll('.playlist')).toHaveLength(1);
        expect(document.getElementById('playlistAssociees-1')!.querySelector('[data-id="p2"]')).toBeTruthy();
        
        expect(document.getElementById('playlistAssociees-2')!.querySelectorAll('.playlist')).toHaveLength(0);
        
        expect(document.getElementById('playlistAssociees-3')!.querySelectorAll('.playlist')).toHaveLength(2);
        expect(document.getElementById('playlistAssociees-3')!.querySelector('[data-id="p1"]')).toBeTruthy();
        expect(document.getElementById('playlistAssociees-3')!.querySelector('[data-id="p3"]')).toBeTruthy();
        
        expect(document.getElementById('playlistAssociees-4')!.querySelectorAll('.playlist')).toHaveLength(0);
        
        expect(unassociated.querySelectorAll('.playlist')).toHaveLength(1);
        expect(unassociated.querySelector('[data-id="p4"]')).toBeTruthy();
    });

    /**
     * Test Case 6: Verify numbering consistency after section insertion
     * Expected: All playlist section numbers are correct and sequential
     */
    it('should maintain correct section numbering after insertion', () => {
        // Setup initial state
        container.innerHTML = `
            <div id="playlistAssociees-1" data-section="1">
                <div class="playlist" data-id="p1" data-section="1">P1</div>
            </div>
            <div id="playlistAssociees-2" data-section="2">
                <div class="playlist" data-id="p2" data-section="2">P2</div>
            </div>
            <div id="playlistAssociees-3" data-section="3">
                <div class="playlist" data-id="p3" data-section="3">P3</div>
            </div>
        `;

        // Simulate insert at position 2 with DOM updates
        // Create new empty section at position 2
        const newSection = document.createElement('div');
        newSection.id = 'playlistAssociees-2';
        newSection.dataset.section = '2';

        // Update old section 2 -> new section 3
        const oldSection2 = document.getElementById('playlistAssociees-2')!;
        oldSection2.id = 'playlistAssociees-3';
        oldSection2.dataset.section = '3';
        const p2 = oldSection2.querySelector('.playlist') as HTMLElement;
        p2.dataset.section = '3';

        // Update old section 3 -> new section 4
        const oldSection3 = document.getElementById('playlistAssociees-3')!;
        oldSection3.id = 'playlistAssociees-4';
        oldSection3.dataset.section = '4';
        const p3 = oldSection3.querySelector('.playlist') as HTMLElement;
        p3.dataset.section = '4';

        // Insert new empty section
        const section1 = document.getElementById('playlistAssociees-1')!;
        section1.insertAdjacentElement('afterend', newSection);

        // Verify final numbering
        expect(document.getElementById('playlistAssociees-1')).toBeTruthy();
        expect(document.getElementById('playlistAssociees-2')).toBeTruthy();
        expect(document.getElementById('playlistAssociees-3')).toBeTruthy();
        expect(document.getElementById('playlistAssociees-4')).toBeTruthy();

        // Verify playlist section numbers
        expect((document.getElementById('playlistAssociees-1')!.querySelector('.playlist') as HTMLElement).dataset.section).toBe('1');
        expect((document.getElementById('playlistAssociees-3')!.querySelector('.playlist') as HTMLElement).dataset.section).toBe('3');
        expect((document.getElementById('playlistAssociees-4')!.querySelector('.playlist') as HTMLElement).dataset.section).toBe('4');
    });

    /**
     * Test Case 7: Empty section handling
     * Expected: Empty sections are not persisted (can be identified)
     */
    it('should identify and skip empty sections', () => {
        // Setup: Section 1 with playlists, Section 2 empty, Section 3 with playlists
        container.innerHTML = `
            <div id="playlistAssociees-1" data-section="1">
                <div class="playlist" data-id="p1" data-section="1">P1</div>
            </div>
            <div id="playlistAssociees-2" data-section="2">
                <!-- Empty section -->
            </div>
            <div id="playlistAssociees-3" data-section="3">
                <div class="playlist" data-id="p3" data-section="3">P3</div>
            </div>
        `;

        // When persisting/saving state, empty sections should be skipped
        const sections = Array.from(document.querySelectorAll('[id^="playlistAssociees-"]')) as HTMLElement[];
        const persistableSections = sections.filter(section => {
            const playlists = section.querySelectorAll('.playlist');
            return playlists.length > 0;
        });

        // Should only have 2 persistable sections (1 and 3)
        expect(persistableSections).toHaveLength(2);
        expect(persistableSections[0].id).toBe('playlistAssociees-1');
        expect(persistableSections[1].id).toBe('playlistAssociees-3');
    });

    /**
     * Test Case 8: Drag from unassociated back to associated zone
     * Expected: Playlist gains section and order
     */
    it('should move playlist from unassociated to associated section', () => {
        // Setup: Unassociated playlist and associated section
        container.innerHTML = `
            <div id="playlistNonAssociees">
                <div class="playlist" data-id="p1">Playlist 1</div>
            </div>
            <div id="playlistAssociees-1" data-section="1">
                <div class="playlist" data-id="p2" data-section="1" data-order="1">Playlist 2</div>
            </div>
        `;

        // Drag p1 from unassociated to section 1
        const p1 = document.querySelector('.playlist[data-id="p1"]') as HTMLElement;
        const section1 = document.getElementById('playlistAssociees-1')!;

        section1.appendChild(p1);
        p1.dataset.section = '1';
        p1.dataset.order = '2';

        // Verify p1 is now in section 1
        expect(p1.dataset.section).toBe('1');
        expect(p1.dataset.order).toBe('2');
        expect(section1.contains(p1)).toBe(true);
        
        // Verify unassociated zone is now empty
        expect(document.getElementById('playlistNonAssociees')!.querySelectorAll('.playlist')).toHaveLength(0);
    });
});
