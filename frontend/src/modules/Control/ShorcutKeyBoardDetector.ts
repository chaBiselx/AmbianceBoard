

class ShorcutKeyBoardDetector {
    private readonly pressedKeys: Set<string>;
    private isListening: boolean;
    private callbackContinue: ((shortcut: string[]) => boolean) | null = null;
    private callbackStop: ((cancel: boolean) => void) | null = null;
    private readonly ignoreList: string[] = ['F12', 'F5'];
    private boundHandleKeyDown: ((event: KeyboardEvent) => void) | null = null;
    private boundHandleKeyUp: ((event: KeyboardEvent) => void) | null = null;

    constructor() {
        this.pressedKeys = new Set();
        this.isListening = false;
    }

    /**
     * Start listening for keyboard shortcuts
     */
    public startListening(callbackContinue: (shortcut: string[]) => boolean = () => {return false}, callbackStop: (cancel: boolean) => void = () => {}): void {
        if (this.isListening) {
            return;
        }
        this.callbackContinue = callbackContinue;
        this.callbackStop = callbackStop;

        this.isListening = true;
        
        // Stocker les références des fonctions bound pour pouvoir les supprimer plus tard
        this.boundHandleKeyDown = this.handleKeyDown.bind(this);
        this.boundHandleKeyUp = this.handleKeyUp.bind(this);
        
        document.addEventListener('keydown', this.boundHandleKeyDown);
        document.addEventListener('keyup', this.boundHandleKeyUp);
    }

    /**
     * Stop listening for keyboard shortcuts
     */
    public stopListening(): void {
        if (!this.isListening) {
            return;
        }

        this.isListening = false;
        
        // Utiliser les références stockées pour supprimer les listeners
        if (this.boundHandleKeyDown) {
            document.removeEventListener('keydown', this.boundHandleKeyDown);
            this.boundHandleKeyDown = null;
        }
        if (this.boundHandleKeyUp) {
            document.removeEventListener('keyup', this.boundHandleKeyUp);
            this.boundHandleKeyUp = null;
        }
        
        this.pressedKeys.clear();
    }

    /**
     * Handle keydown event
     */
    private handleKeyDown(event: KeyboardEvent): void {
        // Add the key to the set of pressed keys
        const key = this.normalizeKey(event.key);

        if (key === 'Escape') {
            this.stopListening();
            if (this.callbackStop) {
                this.callbackStop(true);
            }
            return;
        }

        if (key === 'Delete') {
            this.stopListening();
            if (this.callbackStop) {
                this.callbackStop(false);
            }
            return;
        }

        // Avoid repeating keys when held down
        if (this.pressedKeys.has(key)) {
            return;
        }

        // Allow default behavior for ignored keys
        if(this.ignoreList.includes(key)){
            return;
        }

        event.stopPropagation();

        this.pressedKeys.add(key);

        // Only trigger callback if we have a valid shortcut (not just modifiers)
        if (this.isValidShortcut(event)) {
            const shortcut = this.buildShortcut(event);
            if (this.callbackContinue && shortcut) {
                const action = this.callbackContinue(shortcut);
                if (action === false) {
                    event.preventDefault();
                }
            }
        }
    }

    /**
     * Handle keyup event
     */
    private handleKeyUp(event: KeyboardEvent): void {
        const key = this.normalizeKey(event.key);
        this.pressedKeys.delete(key);
    }

    /**
     * Normalize key names for consistency
     */
    private normalizeKey(key: string): string {
        const keyMap: { [key: string]: string } = {
            'Control': 'Ctrl',
            'Meta': 'Cmd',
            ' ': 'Space',
        };

        return keyMap[key] || key;
    }

    /**
     * Check if the current key combination is a valid shortcut
     * (must have a non-modifier key)
     */
    private isValidShortcut(event: KeyboardEvent): boolean {
        const key = event.key;
        // Return true only if the key pressed is not a modifier key alone
        return !['Control', 'Alt', 'Shift', 'Meta'].includes(key);
    }

    /**
     * Build a human-readable shortcut string
     */
    private buildShortcut(event: KeyboardEvent): string[] {
        const parts: string[] = [];

        if (event.ctrlKey) parts.push('Ctrl');
        if (event.altKey) parts.push('Alt');
        if (event.shiftKey) parts.push('Shift');
        if (event.metaKey) parts.push('Cmd');

        // Add the main key if it's not a modifier
        const key = event.key;
        if (!['Control', 'Alt', 'Shift', 'Meta', 'AltGraph'].includes(key)) {
            parts.push(this.normalizeKey(key));
        }

        return parts;
    }

    /**
     * Get currently pressed keys
     */
    public getPressedKeys(): string[] {
        return Array.from(this.pressedKeys);
    }
}


export default ShorcutKeyBoardDetector;