

class ShorcutKeyBoardDetector {
    private pressedKeys: Set<string>;
    private isListening: boolean;
    private callbackContinue: ((shortcut: string[]) => void) | null = null;
    private callbackStop: (() => void) | null = null;
    private ignoreList: string[] = ['F12'];

    constructor() {
        this.pressedKeys = new Set();
        this.isListening = false;
    }

    /**
     * Start listening for keyboard shortcuts
     */
    public startListening(callbackContinue: (shortcut: string[]) => void = () => {}, callbackStop: () => void = () => {}): void {
        if (this.isListening) {
            return;
        }
        this.callbackContinue = callbackContinue;
        this.callbackStop = callbackStop;

        this.isListening = true;
        document.addEventListener('keydown', this.handleKeyDown.bind(this));
        document.addEventListener('keyup', this.handleKeyUp.bind(this));
    }

    /**
     * Stop listening for keyboard shortcuts
     */
    public stopListening(): void {
        if (!this.isListening) {
            return;
        }

        this.isListening = false;
        document.removeEventListener('keydown', this.handleKeyDown.bind(this));
        document.removeEventListener('keyup', this.handleKeyUp.bind(this));
        this.pressedKeys.clear();
    }

    /**
     * Handle keydown event
     */
    private handleKeyDown(event: KeyboardEvent): void {
        // Prevent ALL default browser behavior immediately when listening
        event.preventDefault();
        event.stopPropagation();
        
        // Add the key to the set of pressed keys
        const key = this.normalizeKey(event.key);

        if (key === 'Escape') {
            this.stopListening();
            if (this.callbackStop) {
                this.callbackStop();
            }
            return;
        }

        // Avoid repeating keys when held down
        if (this.pressedKeys.has(key) || this.ignoreList.includes(key)) {

            return;
        }

        this.pressedKeys.add(key);

        // Only trigger callback if we have a valid shortcut (not just modifiers)
        if (this.isValidShortcut(event)) {
            const shortcut = this.buildShortcut(event);
            if (this.callbackContinue && shortcut) {
                this.callbackContinue(shortcut);
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