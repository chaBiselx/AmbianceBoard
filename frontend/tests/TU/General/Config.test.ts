import { describe, it, expect } from 'vitest';
import Config from '../../../src/modules/General/Config';

describe('Config', () => {
    it('should expose the DEBUG flag from the environment', () => {
        expect(Config).toHaveProperty('DEBUG');
    });

    it('should expose the soundboard players div id', () => {
        expect(Config.SOUNDBOARD_DIV_ID_PLAYERS).toBe('players');
    });
});
