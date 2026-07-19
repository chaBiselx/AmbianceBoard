import * as bootstrap from 'bootstrap';
import ConsoleCustom from "@/modules/General/ConsoleCustom";


class BootstrapComponentInitializer {
    initialize() {
        this.initializeDropdowns();
        this.initializeTooltips();
        this.initializePopovers();
    }

    initializeDropdowns() {
        for (const element of document.querySelectorAll('[data-bs-toggle="dropdown"]')) {
            try {
                new bootstrap.Dropdown(element);
            } catch (error) {
                ConsoleCustom.warn(`Bootstrap Dropdown initialization failed: ${error}`);
            }
        }
    }

    initializeTooltips() {
        for (const element of document.querySelectorAll('[data-bs-toggle="tooltip"]')) {
            try {
                new bootstrap.Tooltip(element);
            } catch (error) {
                ConsoleCustom.warn(`Bootstrap Tooltip initialization failed: ${error}`);
            }
        }
    }

    initializePopovers() {
        for (const element of document.querySelectorAll('[data-bs-toggle="popover"]')) {
            try {
                new bootstrap.Popover(element);
            } catch (error) {
                ConsoleCustom.warn(`Bootstrap Popover initialization failed: ${error}`);
            }
        }
    }

}

export default BootstrapComponentInitializer;