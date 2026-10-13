export type FrontendLocale = 'fr' | 'en';

export type TranslationValues = Record<FrontendLocale, string>;

export const translations: Record<string, TranslationValues> = {
    'onboarding.invitation.title': {
        fr: "Découvrez AmbianceBoard",
        en: 'Discover AmbianceBoard',
    },
    'onboarding.invitation.message': {
        fr: "Envie de découvrir AmbianceBoard avec une visite guidée ?",
        en: 'Would you like a guided tour of AmbianceBoard?',
    },
    'onboarding.invitation.action': {
        fr: 'Commencer la visite',
        en: 'Start the tour',
    },
    'onboarding.invitation.dismiss': {
        fr: 'Fermer',
        en: 'Close',
    },
};

function getLocale(): FrontendLocale {
    const language = document.documentElement.lang.toLowerCase().split('-')[0];
    return language === 'en' ? 'en' : 'fr';
}

export function translate(key: string): string {
    const values = translations[key];
    return values?.[getLocale()] ?? values?.fr ?? key;
}

export default translate;