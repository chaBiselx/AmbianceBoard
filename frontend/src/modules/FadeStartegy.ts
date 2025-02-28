interface FadeStrategyInterface {
    calculateVolume(startVolume:number, endVolume:number, progress:number) : number
}

class FadeStrategy implements FadeStrategyInterface {
    calculateVolume(startVolume:number, endVolume:number, progress:number) : number {
        throw new Error("Méthode calculateVolume doit être implémentée");
    }
}

class LinearFade extends FadeStrategy implements FadeStrategyInterface {
    calculateVolume(startVolume:number, endVolume:number, progress:number) {
        return startVolume + (endVolume - startVolume) * progress;
    }
}

class EaseFade extends FadeStrategy implements FadeStrategyInterface {
    calculateVolume(startVolume:number, endVolume:number, progress:number) {
        return startVolume + (endVolume - startVolume) * (progress < 0.5 ? 2 * progress * progress : 1 - Math.pow(-2 * progress + 2, 2) / 2);
    }
}

class EaseInFade extends FadeStrategy implements FadeStrategyInterface  {
    calculateVolume(startVolume:number, endVolume:number, progress:number) {
        return startVolume + (endVolume - startVolume) * Math.pow(progress, 2);
    }
}

class EaseOutFade extends FadeStrategy implements FadeStrategyInterface  {
    calculateVolume(startVolume:number, endVolume:number, progress:number) {
        return startVolume + (endVolume - startVolume) * (1 - Math.pow(1 - progress, 2));
    }
}

class EaseInQuad extends FadeStrategy implements FadeStrategyInterface  {
    calculateVolume(startVolume:number, endVolume:number, progress:number) {
      return startVolume + (endVolume - startVolume) * progress * progress;
    }
  }
  
  class EaseOutQuad extends FadeStrategy implements FadeStrategyInterface  {
    calculateVolume(startVolume:number, endVolume:number, progress:number) {
      return startVolume + (endVolume - startVolume) * (1 - (1 - progress) * (1 - progress));
    }
  }
  
  class EaseInOutQuad extends FadeStrategy implements FadeStrategyInterface  {
    calculateVolume(startVolume:number, endVolume:number, progress:number) {
      return progress < 0.5
        ? startVolume + (endVolume - startVolume) * 2 * progress * progress
        : startVolume + (endVolume - startVolume) * (1 - Math.pow(-2 * progress + 2, 2) / 2);
    }
  }
  
  class EaseInCubic extends FadeStrategy implements FadeStrategyInterface  {
    calculateVolume(startVolume:number, endVolume:number, progress:number) {
      return startVolume + (endVolume - startVolume) * progress * progress * progress;
    }
  }
  
  class EaseOutCubic extends FadeStrategy implements FadeStrategyInterface  {
    calculateVolume(startVolume:number, endVolume:number, progress:number) {
      return startVolume + (endVolume - startVolume) * (1 - Math.pow(1 - progress, 3));
    }
  }

  class FadeSelector {
    static selectTypeFade(fadeType:string):FadeStrategy {
        
        
        switch (fadeType) {
            case 'linear':
                return new LinearFade();
            case 'ease':
                return new EaseFade();
            case 'ease-in':
                return new EaseInFade();
            case 'ease-out':
                return new EaseOutFade();
            case 'ease-in-quad':
                return new EaseInQuad();
            case 'ease-out-quad':
                return new EaseOutQuad();
            case 'ease-in-out-quad':
                return new EaseInOutQuad();
            case 'ease-in-cubic':
                return new EaseInCubic();
            case 'ease-out-cubic':
                return new EaseOutCubic();
            default:
                return new LinearFade();
        }
    }
}

export default {FadeSelector, FadeStrategy, LinearFade, EaseFade, EaseInFade, EaseOutFade, EaseInQuad, EaseOutQuad, EaseInOutQuad, EaseInCubic, EaseOutCubic };
export type {FadeStrategyInterface};