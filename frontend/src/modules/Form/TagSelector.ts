import ConsoleCustom from '@/modules/General/ConsoleCustom';


class TagSelector {

    private readonly tagBadges: string = '.tag-badge'
    private readonly classSelected: string = 'badge-selected'
    private readonly classUnselected: string = 'badge-unselected'

    public init() {
        const tagBadges = document.querySelectorAll(this.tagBadges);

        for (const badge of tagBadges) {
            badge.addEventListener('click', (e) => {
                this.actionEvent(e);
            });
        }
    }

    private actionEvent(event: Event) {
        event.preventDefault();
        
        if (!event.target) return;
        
        let el = event.target as HTMLElement;
        const tagId = el.dataset.tagId;
        
        if (!tagId) {
            ConsoleCustom.warn('Tag ID not found on element:', el);
            return;
        }
        
        const checkbox = document.getElementById('tag_' + tagId) as HTMLInputElement;
        
        if (!checkbox || checkbox?.type !== "checkbox") {
            ConsoleCustom.warn('Checkbox not found or not a valid input element:', checkbox);
            return;
        }

        // Toggle le checkbox
        checkbox.checked = !checkbox.checked;
        
        // Met à jour l'apparence du badge (appliquer les classes sur le badge, pas sur le checkbox)
        if (checkbox.checked) {
            el.classList.remove(this.classUnselected);
            el.classList.add(this.classSelected);
        } else {
            el.classList.remove(this.classSelected);
            el.classList.add(this.classUnselected);
        }
    }



}

export default TagSelector;