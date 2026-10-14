import { afterEach, describe, expect, it } from 'vitest';
import { translate, translations } from '../../../src/modules/Util/Translation';

describe('translate', () => {
    afterEach(() => {
        document.documentElement.lang = '';
        delete translations['test.greeting'];
    });

    it('returns the French value for a French document', () => {
        document.documentElement.lang = 'fr';
        translations['test.greeting'] = { fr: 'Bonjour', en: 'Hello' };

        expect(translate('test.greeting')).toBe('Bonjour');
    });

    it('returns the English value for an English document', () => {
        document.documentElement.lang = 'en';
        translations['test.greeting'] = { fr: 'Bonjour', en: 'Hello' };

        expect(translate('test.greeting')).toBe('Hello');
    });

    it('uses French for unsupported or missing document languages', () => {
        translations['test.greeting'] = { fr: 'Bonjour', en: 'Hello' };

        expect(translate('test.greeting')).toBe('Bonjour');
        document.documentElement.lang = 'de';
        expect(translate('test.greeting')).toBe('Bonjour');
    });

    it('returns the key when no translation exists', () => {
        expect(translate('missing.key')).toBe('missing.key');
    });
});