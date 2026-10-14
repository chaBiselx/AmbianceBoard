import { EmptyPlaylistChecker, OrganizerDragAndDropZone } from '@/modules/SoundboardOrganizer/OrganizerDom';
import { CleanOrderHandler } from '@/modules/SoundboardOrganizer/PlaylistOrder';
import { SectionAdder, SectionDeleter, SectionRenamer, SectionSwapper } from '@/modules/SoundboardOrganizer/SectionAdder';
import { PointerDragManager } from '@/modules/SoundboardOrganizer/PointerDragManager';
import { ScrollManager } from '@/modules/SoundboardOrganizer/ScrollManager';
import { CommunityPlaylistAdder } from '@/modules/SoundboardOrganizer/CommunityPlaylistAdder';


document.addEventListener("DOMContentLoaded", () => {
    new CommunityPlaylistAdder().addEvent();

    if (OrganizerDragAndDropZone.valid()) {
        new PointerDragManager().setupEvents();
        EmptyPlaylistChecker.check()
        initOrderBadge()
        new SectionAdder(() => new PointerDragManager().setupEvents()).addEvent();
        new SectionDeleter(() => new PointerDragManager().setupEvents()).addEvent();
        new SectionSwapper().addEvent();
        new SectionRenamer().addEvent();
        new ScrollManager().addEvent();
    }
});

function initOrderBadge() {
    const cleanorder = new CleanOrderHandler()
    cleanorder.resetBadge()
}

