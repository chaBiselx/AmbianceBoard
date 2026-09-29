import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import ModalCustom from '../../../src/modules/General/Modal';
import BootstrapComponentInitializer from '../../../src/modules/General/BootstrapComponentInitializer';
import { Modal } from 'bootstrap';

vi.mock('bootstrap', () => {
    function ModalCtor(this: any, element: Element, options: any) {
        this.element = element;
        this.options = options;
        this.show = vi.fn();
        this.hide = vi.fn();
    }
    const ModalMock: any = vi.fn(ModalCtor);
    ModalMock.getInstance = vi.fn();
    return { Modal: ModalMock };
});

vi.mock('@/modules/General/BootstrapComponentInitializer', () => {
    function BootstrapComponentInitializerCtor(this: any) {
        this.initialize = vi.fn();
    }
    const ctor: any = vi.fn(BootstrapComponentInitializerCtor);
    ctor.hideAllTooltips = vi.fn();
    return { default: ctor };
});

function setupDom() {
    document.body.innerHTML = `
        <div id="mainModal">
            <div id="mainModalTitle"></div>
            <div id="mainModalBody"></div>
            <div id="mainModalFooter"></div>
        </div>
        <template id="modal-template-wait"><div class="spinner"></div></template>
    `;
}

describe('ModalCustom', () => {
    beforeEach(() => {
        setupDom();
        vi.mocked(Modal.getInstance).mockReset();
        vi.mocked(Modal).mockClear();
        vi.mocked(BootstrapComponentInitializer.hideAllTooltips).mockClear();
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    it('should return the main modal element', () => {
        expect(ModalCustom.getMainHTMLElement().id).toBe('mainModal');
    });

    it('should return the existing modal instance', () => {
        const instance = { show: vi.fn() };
        vi.mocked(Modal.getInstance).mockReturnValue(instance as any);
        expect(ModalCustom.getInstance()).toBe(instance);
    });

    it('should show a modal with default width and create a new instance when none exists', () => {
        vi.mocked(Modal.getInstance).mockReturnValue(null);

        ModalCustom.show({ title: 'Title', body: 'Body', footer: 'Footer', width: '' });

        expect(Modal).toHaveBeenCalledWith(ModalCustom.getMainHTMLElement(), { keyboard: false });
        expect(document.getElementById('mainModalTitle')!.innerHTML).toBe('Title');
        expect(document.getElementById('mainModalBody')!.innerHTML).toBe('Body');
        expect(document.getElementById('mainModalFooter')!.innerHTML).toBe('Footer');
        expect(BootstrapComponentInitializer.hideAllTooltips).toHaveBeenCalled();
        expect(ModalCustom.getMainHTMLElement().classList.contains('modal-lg')).toBe(false);
    });

    it('should reuse an existing modal instance instead of creating a new one', () => {
        const existingInstance = { show: vi.fn() };
        vi.mocked(Modal.getInstance).mockReturnValue(existingInstance as any);

        ModalCustom.show();

        expect(Modal).not.toHaveBeenCalled();
        expect(existingInstance.show).toHaveBeenCalled();
    });

    it.each([
        ['lg', 'modal-lg'],
        ['sm', 'modal-sm'],
        ['xl', 'modal-xl'],
    ])('should apply the %s width class', (width, expectedClass) => {
        vi.mocked(Modal.getInstance).mockReturnValue(null);

        ModalCustom.show({ title: '', body: '', footer: '', width });

        expect(ModalCustom.getMainHTMLElement().classList.contains(expectedClass)).toBe(true);
    });

    it('should invoke the callback after showing the modal', () => {
        vi.mocked(Modal.getInstance).mockReturnValue(null);
        const callback = vi.fn();

        ModalCustom.show({ title: '', body: '', footer: '', width: '', callback });

        expect(callback).toHaveBeenCalled();
    });

    it('should render the wait template', () => {
        vi.mocked(Modal.getInstance).mockReturnValue(null);

        ModalCustom.wait();

        expect(document.getElementById('mainModalBody')!.innerHTML).toContain('spinner');
    });

    it('should log an error when the wait template is missing', () => {
        document.getElementById('modal-template-wait')!.remove();
        const errorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

        ModalCustom.wait();

        expect(errorSpy).toHaveBeenCalledWith('Template modal-template-wait not found');
    });

    it('should do nothing on hide when there is no modal instance', () => {
        vi.mocked(Modal.getInstance).mockReturnValue(null);
        expect(() => ModalCustom.hide()).not.toThrow();
    });

    it('should hide the modal and clean up its content once hidden', () => {
        const hide = vi.fn();
        vi.mocked(Modal.getInstance).mockReturnValue({ hide } as any);
        document.getElementById('mainModalTitle')!.innerHTML = 'Title';
        document.getElementById('mainModalBody')!.innerHTML = 'Body';
        document.getElementById('mainModalFooter')!.innerHTML = 'Footer';

        ModalCustom.hide();
        expect(hide).toHaveBeenCalled();

        ModalCustom.getMainHTMLElement().dispatchEvent(new Event('hidden.bs.modal'));

        expect(document.getElementById('mainModalTitle')!.innerHTML).toBe('');
        expect(document.getElementById('mainModalBody')!.innerHTML).toBe('');
        expect(document.getElementById('mainModalFooter')!.innerHTML).toBe('');
    });
});
