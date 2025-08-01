import Config from '@/modules/General/Config';

class ConsoleCustom implements Console {
  assert(condition?: boolean, ...data: any[]): void {
    if (Config.DEBUG) {
      console.assert(condition, ...data);
    }
  }
  clear(): void {
    if (Config.DEBUG) {
      console.clear();
    }
  }
  count(label?: string): void {
    if (Config.DEBUG) {
      console.count(label);
    }
  }
  countReset(label?: string): void {
    if (Config.DEBUG) {
      console.countReset(label);
    }
  }
  debug(...data: any[]): void {
    if (Config.DEBUG) {
      console.debug(...data);
    }
  }
  dir(item?: any, options?: any): void {
    if (Config.DEBUG) {
      console.dir(item, options);
    }
  }
  dirxml(...data: any[]): void {
    if (Config.DEBUG) {
      console.dirxml(...data);
    }
  }
  error(...data: any[]): void {
    if (Config.DEBUG) {
      console.error(...data);
    }
  }
  group(...data: any[]): void {
    if (Config.DEBUG) {
      console.group(...data);
    }
  }
  groupCollapsed(...data: any[]): void {
    if (Config.DEBUG) {
      console.groupCollapsed(...data);
    }
  }
  groupEnd(): void {
    if (Config.DEBUG) {
      console.groupEnd();
    }
  }
  info(...data: any[]): void {
    if (Config.DEBUG) {
      console.info(...data);
    }
  }
  log(...data: any[]): void {
    if (Config.DEBUG) {
      console.log(...data);
    }
  }
  table(tabularData?: any, properties?: string[]): void {
    if (Config.DEBUG) {
      console.table(tabularData, properties);
    }
  }
  time(label?: string): void {
    if (Config.DEBUG) {
      console.time(label);
    }
  }
  timeEnd(label?: string): void {
    if (Config.DEBUG) {
      console.timeEnd(label);
    }
  }
  timeLog(label?: string, ...data: any[]): void {
    if (Config.DEBUG) {
      console.timeLog(label, ...data);
    }
  }
  timeStamp(label?: string): void {
    if (Config.DEBUG) {
      console.timeStamp(label);
    }
  }
  trace(...data: any[]): void {
    if (Config.DEBUG) {
      console.trace(...data);
    }
  }
  warn(...data: any[]): void {
    if (Config.DEBUG) {
      console.warn(...data);
    }
  }

}

export default new ConsoleCustom();