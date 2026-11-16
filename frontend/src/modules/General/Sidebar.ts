class Sidebar {
    sidebarToggle: HTMLButtonElement | null = null
    sidebar: HTMLDivElement | null = null

    constructor() {
        this.sidebarToggle = document.querySelector<HTMLButtonElement>('.navbar-toggler');
        this.sidebar = document.querySelector<HTMLDivElement>('.sidebar');
    }

    public addEvent() {
        if (this.sidebarToggle && this.sidebar) {
            this.sidebarToggle.addEventListener('click', this.toggle.bind(this));
        }
    }

    public toggle() {
        if (this.sidebar) {
            this.sidebar.classList.toggle('d-block');
        }
    }
}

export default Sidebar;
