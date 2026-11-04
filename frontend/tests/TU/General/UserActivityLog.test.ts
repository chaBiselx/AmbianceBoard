import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import UserActivityLog from '../../../src/modules/General/UserActivityLog';
import Csrf from '../../../src/modules/General/Csrf';
import Time from '../../../src/modules/Util/Time';

vi.mock('@/modules/General/Csrf', () => ({
    default: { getToken: vi.fn() },
}));

describe('UserActivityLog', () => {
    beforeEach(() => {
        document.body.innerHTML = '<div id="trace_user_activity" data-url="/activity"></div>';
        vi.clearAllMocks();
        vi.mocked(Csrf.getToken).mockReturnValue('csrf-token');
    });

    afterEach(() => {
        vi.useRealTimers();
        vi.unstubAllGlobals();
        vi.restoreAllMocks();
    });

    it('posts activity on page exit and every fifteen minutes', () => {
        vi.useFakeTimers();
        const fetchMock = vi.fn().mockResolvedValue({});
        vi.stubGlobal('fetch', fetchMock);
        new UserActivityLog().addEvent();

        window.dispatchEvent(new Event('beforeunload'));
        expect(fetchMock).toHaveBeenCalledWith('/activity', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': 'csrf-token' },
        });

        vi.advanceTimersByTime(Time.get_minutes(15));
        expect(fetchMock).toHaveBeenCalledTimes(2);
    });
});
