interface FadeStrategyInterface {
    calculateVolume(startVolume: number, endVolume: number, progress: number): number
}

abstract class FadeStrategy implements FadeStrategyInterface {
    abstract calculateVolume(startVolume: number, endVolume: number, progress: number): number
}

class LinearFade extends FadeStrategy implements FadeStrategyInterface {
    calculateVolume(startVolume: number, endVolume: number, progress: number) {
        return startVolume + (endVolume - startVolume) * progress;
    }
}

class EaseFade extends FadeStrategy implements FadeStrategyInterface {
    calculateVolume(startVolume: number, endVolume: number, progress: number) {
        return startVolume + (endVolume - startVolume) * (progress < 0.5 ? 2 * progress * progress : 1 - Math.pow(-2 * progress + 2, 2) / 2);
    }
}

class EaseInFade extends FadeStrategy implements FadeStrategyInterface {
    calculateVolume(startVolume: number, endVolume: number, progress: number) {
        return startVolume + (endVolume - startVolume) * Math.pow(progress, 2);
    }
}

class EaseOutFade extends FadeStrategy implements FadeStrategyInterface {
    calculateVolume(startVolume: number, endVolume: number, progress: number) {
        return startVolume + (endVolume - startVolume) * (1 - Math.pow(1 - progress, 2));
    }
}

class EaseInQuad extends FadeStrategy implements FadeStrategyInterface {
    calculateVolume(startVolume: number, endVolume: number, progress: number) {
        return startVolume + (endVolume - startVolume) * progress * progress;
    }
}

class EaseOutQuad extends FadeStrategy implements FadeStrategyInterface {
    calculateVolume(startVolume: number, endVolume: number, progress: number) {
        return startVolume + (endVolume - startVolume) * (1 - (1 - progress) * (1 - progress));
    }
}

class EaseInOutQuad extends FadeStrategy implements FadeStrategyInterface {
    calculateVolume(startVolume: number, endVolume: number, progress: number) {
        return progress < 0.5
            ? startVolume + (endVolume - startVolume) * 2 * progress * progress
            : startVolume + (endVolume - startVolume) * (1 - Math.pow(-2 * progress + 2, 2) / 2);
    }
}

class EaseInCubic extends FadeStrategy implements FadeStrategyInterface {
    calculateVolume(startVolume: number, endVolume: number, progress: number) {
        return startVolume + (endVolume - startVolume) * progress * progress * progress;
    }
}

class EaseOutCubic extends FadeStrategy implements FadeStrategyInterface {
    calculateVolume(startVolume: number, endVolume: number, progress: number) {
        return startVolume + (endVolume - startVolume) * (1 - Math.pow(1 - progress, 3));
    }
}

class FadeSelector {

    private static readonly strategies: Record<string, FadeStrategyInterface> = {
        'linear': new LinearFade(),
        'ease': new EaseFade(),
        'ease-in': new EaseInFade(),
        'ease-out': new EaseOutFade(),
        'ease-in-quad': new EaseInQuad(),
        'ease-out-quad': new EaseOutQuad(),
        'ease-in-out-quad': new EaseInOutQuad(),
        'ease-in-cubic': new EaseInCubic(),
        'ease-out-cubic': new EaseOutCubic()
    };
    static selectTypeFade(fadeType: string): FadeStrategy {
        return this.strategies[fadeType] ?? this.strategies['linear'];
    }
}

export default { FadeSelector, FadeStrategy, LinearFade, EaseFade, EaseInFade, EaseOutFade, EaseInQuad, EaseOutQuad, EaseInOutQuad, EaseInCubic, EaseOutCubic };
export type { FadeStrategyInterface };