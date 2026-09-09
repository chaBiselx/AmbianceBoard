import { EmptyPlaylistChecker, OrganizerDragAndDropZone } from '@/modules/SoundboardOrganizer/OrganizerDom';
import { CleanOrderHandler } from '@/modules/SoundboardOrganizer/PlaylistOrder';
import { SectionAdder } from '@/modules/SoundboardOrganizer/SectionAdder';
import { PointerDragManager } from '@/modules/SoundboardOrganizer/PointerDragManager';
import { ScrollManager } from '@/modules/SoundboardOrganizer/ScrollManager';


document.addEventListener("DOMContentLoaded", () => {
    if (OrganizerDragAndDropZone.valid()) {
        new PointerDragManager().setupEvents();
        EmptyPlaylistChecker.check()
        initOrderBadge()
        new SectionAdder(() => new PointerDragManager().setupEvents()).addEvent();
        new ScrollManager().addEvent();
    }
});

function initOrderBadge() {
    const cleanorder = new CleanOrderHandler()
    cleanorder.resetBadge()
}




