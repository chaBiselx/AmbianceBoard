
class ConsoleTesteur implements Console {
    DOM: HTMLElement | null;
    private readonly counters: Map<string, number> = new Map();
    private readonly timers: Map<string, number> = new Map();
    private groupLevel: number = 0;

    constructor() {
        this.DOM = document.getElementById('console-testeur');
        this.initializeStyles();
    }

    private valid(): boolean {
        return this.DOM !== null;
    }

    private initializeStyles(): void {
        if (!this.valid()) return;

        // Ajouter les styles CSS pour la console
        const style = document.createElement('style');
        style.textContent = `
            .console-testeur {
                font-family: 'Courier New', monospace;
                font-size: 12px;
                line-height: 1.4;
                background: #1e1e1e;
                color: #d4d4d4;
                padding: 10px;
                border-radius: 4px;
                max-height: 400px;
                overflow-y: auto;
                white-space: pre-wrap;
            }
            .console-timestamp { color: #7a7a7aff; }
            .console-log { color: #d4d4d4; }
            .console-error { color: #f14c4c; }
            .console-warn { color: #ffcc02; }
            .console-info { color: #3794ff; }
            .console-debug { color: #b267e6; }
            .console-group { margin-left: 20px; }
            .console-time { color: #4fc1ff; }
            .console-trace { color: #ff8c00; }
        `;
        document.head.appendChild(style);

        // Initialiser la classe CSS sur le DOM
        this.DOM!.classList.add('console-testeur');
    }

    private writeToDOM(message: string, className: string = 'console-log'): void {
        if (!this.valid()) return;

        const timestamp = new Date().toLocaleTimeString();
        const div = document.createElement('div');
        div.className = className;
        div.style.marginLeft = `${this.groupLevel * 20}px`;
        div.innerHTML = `<span class="console-timestamp">[${timestamp}]</span> ${message}`;

        this.DOM!.appendChild(div);
        this.DOM!.scrollTop = this.DOM!.scrollHeight;
    }

    private formatData(...data: any[]): string {
        return data.map(item => {
            if (typeof item === 'object') {
                try {
                    return JSON.stringify(item, null, 2);
                } catch {
                    return String(item);
                }
            }
            return String(item);
        }).join(' ');
    }

    assert(condition?: boolean, ...data: any[]): void {
        if (!condition) {
            this.writeToDOM(`Assertion failed: ${this.formatData(...data)}`, 'console-error');
        }
    }

    clear(): void {
        if (this.valid()) {
            this.DOM!.innerHTML = '';
        }
    }

    count(label: string = 'default'): void {
        const key = label;
        const current = this.counters.get(key) || 0;
        this.counters.set(key, current + 1);
        this.writeToDOM(`${key}: ${current + 1}`, 'console-info');
    }

    countReset(label: string = 'default'): void {
        const key = label;
        this.counters.set(key, 0);
        this.writeToDOM(`${key}: 0`, 'console-info');
    }

    debug(...data: any[]): void {
        this.writeToDOM(this.formatData(...data), 'console-debug');
    }

    dir(item?: any, _options?: any): void {
        const formatted = typeof item === 'object' ?
            JSON.stringify(item, null, 2) :
            String(item);
        this.writeToDOM(formatted, 'console-info');
    }

    dirxml(...data: any[]): void {
        this.writeToDOM(this.formatData(...data), 'console-info');
    }

    error(...data: any[]): void {
        this.writeToDOM(this.formatData(...data), 'console-error');
    }

    group(...data: any[]): void {
        if (data.length > 0) {
            this.writeToDOM(`▼ ${this.formatData(...data)}`, 'console-log');
        }
        this.groupLevel++;
    }

    groupCollapsed(...data: any[]): void {
        if (data.length > 0) {
            this.writeToDOM(`▶ ${this.formatData(...data)}`, 'console-log');
        }
        this.groupLevel++;
    }

    groupEnd(): void {
        if (this.groupLevel > 0) {
            this.groupLevel--;
        }
    }

    info(...data: any[]): void {
        this.writeToDOM(this.formatData(...data), 'console-info');
    }

    log(...data: any[]): void {
        this.writeToDOM(this.formatData(...data), 'console-log');
    }

    table(tabularData?: any, properties?: string[]): void {
        if (Array.isArray(tabularData)) {
            const table = tabularData.map((row, index) => {
                const cols = properties ?
                    properties.map(prop => row[prop]).join(' | ') :
                    Object.values(row).join(' | ');
                return `${index}: ${cols}`;
            }).join('\n');
            this.writeToDOM(`Table:\n${table}`, 'console-log');
        } else {
            this.writeToDOM(this.formatData(tabularData), 'console-log');
        }
    }

    time(label: string = 'default'): void {
        const key = label;
        this.timers.set(key, performance.now());
        this.writeToDOM(`Timer '${key}' started`, 'console-time');
    }

    timeEnd(label: string = 'default'): void {
        const key = label;
        const startTime = this.timers.get(key);
        if (startTime === undefined) {
            this.writeToDOM(`Timer '${key}' does not exist`, 'console-warn');
        } else {
            const duration = performance.now() - startTime;
            this.writeToDOM(`${key}: ${duration.toFixed(3)}ms`, 'console-time');
            this.timers.delete(key);
        }
    }

    timeLog(label: string = 'default', ...data: any[]): void {
        const key = label;
        const startTime = this.timers.get(key);
        if (startTime === undefined) {
            this.writeToDOM(`Timer '${key}' does not exist`, 'console-warn');
        } else {
            const duration = performance.now() - startTime;
            const message = data.length > 0 ?
                `${key}: ${duration.toFixed(3)}ms ${this.formatData(...data)}` :
                `${key}: ${duration.toFixed(3)}ms`;
            this.writeToDOM(message, 'console-time');
        }
    }

    timeStamp(label?: string): void {
        const timestamp = performance.now();
        const message = label ?
            `${label} @${timestamp.toFixed(3)}ms` :
            `Timestamp @${timestamp.toFixed(3)}ms`;
        this.writeToDOM(message, 'console-time');
    }

    trace(...data: any[]): void {
        const stack = new Error("Console trace").stack || 'No stack trace available';
        const message = data.length > 0 ?
            `${this.formatData(...data)}\n${stack}` :
            stack;
        this.writeToDOM(message, 'console-trace');
    }

    warn(...data: any[]): void {
        this.writeToDOM(this.formatData(...data), 'console-warn');
    }

}

export default new ConsoleTesteur();