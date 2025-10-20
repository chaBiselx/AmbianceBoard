import ConsoleCustom from "@/modules/General/ConsoleCustom";


class ConsoleTesteur implements Console {
    DOM: HTMLElement | null;
    private readonly counters: Map<string, number> = new Map();
    private readonly timers: Map<string, number> = new Map();
    private groupLevel: number = 0;

    constructor() {
        this.DOM = document.getElementById('console-testeur');
        const clearButton = document.getElementById('clear-console-testeur');
        if (clearButton) {
            clearButton.addEventListener('click', () => this.clearConsole());
        }
    }

    private valid(): boolean {
        return this.DOM !== null;
    }

    private clearConsole(): void {
        if (this.valid()) {
            this.DOM!.innerHTML = '';
        }
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
        ConsoleCustom.assert(condition, ...data); // Keep original behavior
        if (!condition) {
            this.writeToDOM(`Assertion failed: ${this.formatData(...data)}`, 'console-error');
        }
    }

    clear(): void {
        ConsoleCustom.clear(); // Keep original behavior
        if (this.valid()) {
            this.DOM!.innerHTML = '';
        }
    }

    count(label: string = 'default'): void {
        ConsoleCustom.count(label);
        const key = label;
        const current = this.counters.get(key) || 0;
        this.counters.set(key, current + 1);
        this.writeToDOM(`${key}: ${current + 1}`, 'console-info');
    }

    countReset(label: string = 'default'): void {
        ConsoleCustom.countReset(label);
        const key = label;
        this.counters.set(key, 0);
        this.writeToDOM(`${key}: 0`, 'console-info');
    }

    debug(...data: any[]): void {
        ConsoleCustom.debug(...data);
        this.writeToDOM(this.formatData(...data), 'console-debug');
    }

    dir(item?: any, _options?: any): void {
        ConsoleCustom.dir(item, _options);
        const formatted = typeof item === 'object' ?
            JSON.stringify(item, null, 2) :
            String(item);
        this.writeToDOM(formatted, 'console-info');
    }

    dirxml(...data: any[]): void {
        ConsoleCustom.dirxml(...data);
        this.writeToDOM(this.formatData(...data), 'console-info');
    }

    error(...data: any[]): void {
        ConsoleCustom.error(...data);
        this.writeToDOM(this.formatData(...data), 'console-error');
    }

    group(...data: any[]): void {
        ConsoleCustom.group(...data);
        if (data.length > 0) {
            this.writeToDOM(`▼ ${this.formatData(...data)}`, 'console-log');
        }
        this.groupLevel++;
    }

    groupCollapsed(...data: any[]): void {
        ConsoleCustom.groupCollapsed(...data);
        if (data.length > 0) {
            this.writeToDOM(`▶ ${this.formatData(...data)}`, 'console-log');
        }
        this.groupLevel++;
    }

    groupEnd(): void {
        ConsoleCustom.groupEnd();
        if (this.groupLevel > 0) {
            this.groupLevel--;
        }
    }

    info(...data: any[]): void {
        ConsoleCustom.info(...data);
        this.writeToDOM(this.formatData(...data), 'console-info');
    }

    log(...data: any[]): void {
        ConsoleCustom.log(...data);
        this.writeToDOM(this.formatData(...data), 'console-log');
    }

    table(tabularData?: any, properties?: string[]): void {
        ConsoleCustom.table(tabularData, properties);
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
        ConsoleCustom.time(label);
        const key = label;
        this.timers.set(key, performance.now());
        this.writeToDOM(`Timer '${key}' started`, 'console-time');
    }

    timeEnd(label: string = 'default'): void {
        ConsoleCustom.timeEnd(label);
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
        ConsoleCustom.timeLog(label, ...data);
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
        ConsoleCustom.timeStamp(label);
        const timestamp = performance.now();
        const message = label ?
            `${label} @${timestamp.toFixed(3)}ms` :
            `Timestamp @${timestamp.toFixed(3)}ms`;
        this.writeToDOM(message, 'console-time');
    }

    trace(...data: any[]): void {
        ConsoleCustom.trace(...data);
        const stack = new Error("Console trace").stack || 'No stack trace available';
        const message = data.length > 0 ?
            `${this.formatData(...data)}\n${stack}` :
            stack;
        this.writeToDOM(message, 'console-trace');
    }

    warn(...data: any[]): void {
        ConsoleCustom.warn(...data);
        this.writeToDOM(this.formatData(...data), 'console-warn');
    }

}

export default new ConsoleTesteur();