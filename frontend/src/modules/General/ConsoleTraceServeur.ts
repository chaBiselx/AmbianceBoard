import Config from '@/modules/General/Config';
import Csrf from '@/modules/General/Csrf';

class ConsoleTraceServeur implements Console {
    private readonly uriTrace: string = '/trace-front';
    assert(_condition?: boolean, ..._data: any[]): void { }  // NOSONAR
    clear(): void { } // NOSONAR
    count(_label?: string): void { } // NOSONAR
    countReset(_label?: string): void { } // NOSONAR
    debug(...data: any[]): void {
        this.sendTraceToServer('debug', data);
    }
    dir(_item?: any, _options?: any): void { } // NOSONAR
    dirxml(..._data: any[]): void { } // NOSONAR
    error(...data: any[]): void { // NOSONAR
        this.sendTraceToServer('error', data);
    }
    group(..._data: any[]): void { } // NOSONAR
    groupCollapsed(..._data: any[]): void { } // NOSONAR
    groupEnd(): void { } // NOSONAR
    info(...data: any[]): void {
        this.sendTraceToServer('info', data);
    }
    log(...data: any[]): void {
        this.sendTraceToServer('log', data);
    }
    table(_tabularData?: any, _properties?: string[]): void { } // NOSONAR
    time(_label?: string): void { } // NOSONAR
    timeEnd(_label?: string): void { } // NOSONAR
    timeLog(_label?: string, ..._data: any[]): void { } // NOSONAR
    timeStamp(_label?: string): void { } // NOSONAR
    trace(...data: any[]): void {
        this.sendTraceToServer('trace', data);
    }
    warn(...data: any[]): void {
        this.sendTraceToServer('warn', data);
    }

    private sendTraceToServer(level: string, messages: any[]): void {
        const debugInfo = {
            userAgent: navigator.userAgent
        };
        messages.push(debugInfo);

        const url = globalThis.location.origin + this.uriTrace;
        console.log(url);
        const csrfToken = Csrf.getToken();
        if (url && csrfToken) {
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    level: level,
                    messages: messages,
                    timestamp: new Date().toISOString()
                })
            }).catch((error) => {
                if (Config.DEBUG) {
                    console.error('Failed to send trace to server:', error);
                }
            });
        }

    }

}

export default new ConsoleTraceServeur();