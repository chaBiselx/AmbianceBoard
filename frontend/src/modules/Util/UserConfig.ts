

class UserConfig {
    public static detectKeyboard(): boolean {
        // Vérifier si l'appareil a un clavier physique
        // Les appareils tactiles purs n'ont généralement pas de clavier physique

        // Vérifier si c'est un appareil tactile
        const isTouchDevice = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0);

        // Vérifier le type de pointeur principal
        const hasCoarsePointer = window.matchMedia('(pointer: coarse)').matches;

        // Si c'est un appareil tactile avec pointeur grossier, probablement sans clavier
        if (isTouchDevice && hasCoarsePointer) {
            return false;
        }

        // Par défaut, on considère qu'un clavier est disponible
        return true;
    }
}


export default UserConfig;