import { afterEach, beforeEach, vi } from 'vitest';
import Csrf from '../../../src/modules/General/Csrf';

export function setupAccountTestHooks() {
    beforeEach(() => {
        vi.clearAllMocks();
        vi.mocked(Csrf.getToken).mockReturnValue('csrf-token');
    });

    afterEach(() => {
        vi.unstubAllGlobals();
        vi.restoreAllMocks();
    });
}
