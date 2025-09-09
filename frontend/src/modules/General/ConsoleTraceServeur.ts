import Config from '@/modules/General/Config';
import Csrf from '@/modules/General/Csrf';

class ConsoleTraceServeur implements Console {
    private readonly uriTrace: string = '/trace-front';
    assert(_condition?: boolean, ..._data: any[]): void {}
    clear(): void {}
    count(_label?: string): void {}
    countReset(_label?: string): void {}
    debug(...data: any[]): void {
        this.sendTraceToServer('debug', data);
    }
    dir(_item?: any, _options?: any): void {}
    dirxml(..._data: any[]): void {}
    error(...data: any[]): void {
        this.sendTraceToServer('error', data);
    }
    group(..._data: any[]): void {}
    groupCollapsed(..._data: any[]): void {}
    groupEnd(): void {}
    info(...data: any[]): void {
        this.sendTraceToServer('info', data);
    }
    log(...data: any[]): void {
        this.sendTraceToServer('log', data);
    }
    table(_tabularData?: any, _properties?: string[]): void {}
    time(_label?: string): void {}
    timeEnd(_label?: string): void {}
    timeLog(_label?: string, ..._data: any[]): void {}
    timeStamp(_label?: string): void {}
    trace(...data: any[]): void {
        this.sendTraceToServer('trace', data);
    }
    warn(...data: any[]): void {
        this.sendTraceToServer('warn', data);
    }

    private sendTraceToServer(level: string, messages: any[]): void {
        const url = window.location.origin + this.uriTrace;
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