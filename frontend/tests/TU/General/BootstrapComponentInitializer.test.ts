import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import BootstrapComponentInitializer from '../../../src/modules/General/BootstrapComponentInitializer';
import ConsoleCustom from '../../../src/modules/General/ConsoleCustom';
import * as bootstrap from 'bootstrap';

vi.mock('@/modules/General/ConsoleCustom', () => ({
    default: { warn: vi.fn() },
}));

vi.mock('bootstrap', () => {
    class Dropdown {
        constructor(public element: Element) {}
    }
    class Tooltip {
        constructor(public element: Element) {}
        hide = vi.fn();
        static getInstance = vi.fn();
    }
    class Popover {
        constructor(public element: Element) {}
    }
    return { Dropdown, Tooltip, Popover };
});

describe('BootstrapComponentInitializer', () => {
    beforeEach(() => {
        document.body.innerHTML = '';
        vi.mocked(bootstrap.Tooltip.getInstance).mockReset();
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    it('should initialize dropdowns, tooltips and popovers', () => {
        document.body.innerHTML = `
            <div data-bs-toggle="dropdown"></div>
            <div data-bs-toggle="tooltip"></div>
            <div data-bs-toggle="popover"></div>
        `;

        expect(() => new BootstrapComponentInitializer().initialize()).not.toThrow();
    });

    it('should warn and continue when a dropdown fails to initialize', () => {
        document.body.innerHTML = `<div data-bs-toggle="dropdown"></div>`;
        vi.spyOn(bootstrap, 'Dropdown').mockImplementation(() => {
            throw new Error('boom');
        });

        new BootstrapComponentInitializer().initializeDropdowns();

        expect(ConsoleCustom.warn).toHaveBeenCalledWith(expect.stringContaining('Bootstrap Dropdown initialization failed'));
    });

    it('should warn and continue when a tooltip fails to initialize', () => {
        document.body.innerHTML = `<div data-bs-toggle="tooltip"></div>`;
        vi.spyOn(bootstrap, 'Tooltip').mockImplementation(() => {
            throw new Error('boom');
        });

        new BootstrapComponentInitializer().initializeTooltips();

        expect(ConsoleCustom.warn).toHaveBeenCalledWith(expect.stringContaining('Bootstrap Tooltip initialization failed'));
    });

    it('should warn and continue when a popover fails to initialize', () => {
        document.body.innerHTML = `<div data-bs-toggle="popover"></div>`;
        vi.spyOn(bootstrap, 'Popover').mockImplementation(() => {
            throw new Error('boom');
        });

        new BootstrapComponentInitializer().initializePopovers();

        expect(ConsoleCustom.warn).toHaveBeenCalledWith(expect.stringContaining('Bootstrap Popover initialization failed'));
    });

    it('should hide and blur every visible tooltip and remove stale tooltip nodes', () => {
        document.body.innerHTML = `
            <div data-bs-toggle="tooltip"></div>
            <div class="tooltip show"></div>
        `;
        const hideMock = vi.fn();
        vi.mocked(bootstrap.Tooltip.getInstance).mockReturnValue({ hide: hideMock } as any);

        BootstrapComponentInitializer.hideAllTooltips();

        expect(hideMock).toHaveBeenCalled();
        expect(document.querySelector('.tooltip.show')).toBeNull();
    });

    it('should skip hiding when there is no tooltip instance attached', () => {
        document.body.innerHTML = `<div data-bs-toggle="tooltip"></div>`;
        vi.mocked(bootstrap.Tooltip.getInstance).mockReturnValue(null);

        expect(() => BootstrapComponentInitializer.hideAllTooltips()).not.toThrow();
    });

    it('should only attach the modal tooltip guards once', () => {
        document.body.innerHTML = `
            <div data-bs-toggle="tooltip"></div>
        `;
        const hideSpy = vi.spyOn(BootstrapComponentInitializer, 'hideAllTooltips').mockImplementation(() => {});

        new BootstrapComponentInitializer().initialize();
        new BootstrapComponentInitializer().initialize();

        document.dispatchEvent(new Event('show.bs.modal'));
        document.dispatchEvent(new Event('hide.bs.modal'));

        expect(hideSpy).toHaveBeenCalledTimes(2);
    });
});
