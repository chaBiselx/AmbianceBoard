import * as bootstrap from 'bootstrap';
import ConsoleCustom from "@/modules/General/ConsoleCustom";


class BootstrapComponentInitializer {
    private static modalTooltipGuardsAttached = false;

    initialize() {
        this.initializeDropdowns();
        this.initializeTooltips();
        this.initializePopovers();
        this.attachModalTooltipGuards();
    }

    public static hideAllTooltips() {
        for (const element of document.querySelectorAll('[data-bs-toggle="tooltip"]')) {
            const htmlElement = element as HTMLElement;
            const tooltip = bootstrap.Tooltip.getInstance(htmlElement);

            if (tooltip) {
                tooltip.hide();
            }

            htmlElement.blur();
        }

        // Defensive cleanup for stale tooltip DOM nodes left after interrupted transitions.
        for (const tooltipElement of document.querySelectorAll('.tooltip.show')) {
            tooltipElement.remove();
        }
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

    private attachModalTooltipGuards() {
        if (BootstrapComponentInitializer.modalTooltipGuardsAttached) {
            return;
        }

        BootstrapComponentInitializer.modalTooltipGuardsAttached = true;

        document.addEventListener('show.bs.modal', () => {
            BootstrapComponentInitializer.hideAllTooltips();
        });

        document.addEventListener('hide.bs.modal', () => {
            BootstrapComponentInitializer.hideAllTooltips();
        });
    }

}

export default BootstrapComponentInitializer;