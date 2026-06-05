import ConsoleCustom from '@/modules/General/ConsoleCustom';
import FadeModule from '@/modules/FadeStartegy';

type DefaultFadeConfig = {
    fadeIn?: string;
    fadeOut?: string;
};

type CurveColors = {
    IN: string;
    OUT: string;
    AXIS: string;
    BG: string;
    MUTED: string;
};

type FadeStrategy = { calculateVolume(startVolume: number, endVolume: number, progress: number): number };

const FADE_ENUM_TO_STRATEGY: Record<string, string> = {
    DISABLED: 'disabled',
    LINEAR: 'linear',
    EASE: 'ease',
    EASE_IN: 'ease-in',
    EASE_OUT: 'ease-out',
    EASE_IN_QUAD: 'ease-in-quad',
    EASE_OUT_QUAD: 'ease-out-quad',
    EASE_IN_OUT_QUAD: 'ease-in-out-quad',
    EASE_OUT_CUBIC: 'ease-out-cubic',
};

export default class MergedFadePreviewCanvasRenderer {
    renderFromDom(): void {
        const fadeInSelect = document.getElementById('id_fadeIn') as HTMLSelectElement | null;
        const fadeOutSelect = document.getElementById('id_fadeOut') as HTMLSelectElement | null;
        const typeSelect = document.getElementById('id_typePlaylist') as HTMLSelectElement | null;
        const canvas = document.getElementById('canvas-fade-merged') as HTMLCanvasElement | null;
        const messageEl = document.getElementById('fade-merged-preview-msg');
        const legendEl = document.getElementById('fade-merged-preview-legend');

        if (!fadeInSelect || !fadeOutSelect || !typeSelect || !canvas || !messageEl || !legendEl) {
            return;
        }

        const ctx = canvas.getContext('2d');
        if (!ctx) {
            return;
        }

        this.syncCanvasSize(canvas, ctx);

        const defaultFadesByType = this.parseDefaultFadesByType(typeSelect);
        const selectedType = typeSelect.value;
        const effectiveFadeIn = this.resolveFadeValue(fadeInSelect.value, selectedType, defaultFadesByType, 'fadeIn');
        const effectiveFadeOut = this.resolveFadeValue(fadeOutSelect.value, selectedType, defaultFadesByType, 'fadeOut');
        const normalizedFadeIn = this.normalizeFadeValue(effectiveFadeIn);
        const normalizedFadeOut = this.normalizeFadeValue(effectiveFadeOut);
        const colors = this.getCurveColorMap();

        const width = Math.max(1, canvas.clientWidth);
        const height = Math.max(1, canvas.clientHeight || 90);
        const padding = 8;
        const drawWidth = width - padding * 2;
        const drawHeight = height - padding * 2;

        ctx.clearRect(0, 0, width, height);
        ctx.fillStyle = colors.BG;
        ctx.fillRect(0, 0, width, height);

        ctx.strokeStyle = colors.AXIS;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(padding, padding);
        ctx.lineTo(padding, height - padding);
        ctx.lineTo(width - padding, height - padding);
        ctx.stroke();

        const messages: string[] = [];

        if (normalizedFadeIn === 'disabled') {
            this.drawOffLine(ctx, colors.IN, padding, width, height, 2.6);
        } else {
            try {
                this.drawCurve(
                    ctx,
                    FadeModule.FadeSelector.selectTypeFade(normalizedFadeIn),
                    colors.IN,
                    0,
                    1,
                    padding,
                    drawWidth,
                    drawHeight,
                    height,
                    2.6,
                );
            } catch {
                messages.push('Fade in non reconnu ' + effectiveFadeIn);
            }
        }

        if (normalizedFadeOut === 'disabled') {
            this.drawOffLine(ctx, colors.OUT, padding, width, height, 2.6);
        } else {
            try {
                this.drawCurve(
                    ctx,
                    FadeModule.FadeSelector.selectTypeFade(normalizedFadeOut),
                    colors.OUT,
                    1,
                    0,
                    padding,
                    drawWidth,
                    drawHeight,
                    height,
                    2.6,
                );
            } catch {
                messages.push('Fade out non reconnu ' + effectiveFadeOut);
            }
        }

        const fadeInOptionLabel = fadeInSelect.options[fadeInSelect.selectedIndex]?.textContent?.trim() || fadeInSelect.value;
        const fadeOutOptionLabel = fadeOutSelect.options[fadeOutSelect.selectedIndex]?.textContent?.trim() || fadeOutSelect.value;
        const fadeInLegendLabel = fadeInSelect.value === 'DEFAULT'
            ? 'Par défaut'
            : fadeInOptionLabel;
        const fadeOutLegendLabel = fadeOutSelect.value === 'DEFAULT'
            ? 'Par défaut'
            : fadeOutOptionLabel;

        this.renderMergedFadeLegend(legendEl, fadeInLegendLabel, fadeOutLegendLabel, colors);
        messageEl.textContent = messages.join(' | ');
    }

    private syncCanvasSize(canvas: HTMLCanvasElement, ctx: CanvasRenderingContext2D): void {
        const cssWidth = Math.max(1, Math.floor(canvas.clientWidth));
        const cssHeight = Math.max(1, Math.floor(canvas.clientHeight || 90));
        const pixelRatio = Math.max(1, window.devicePixelRatio || 1);
        const nextWidth = Math.floor(cssWidth * pixelRatio);
        const nextHeight = Math.floor(cssHeight * pixelRatio);

        if (canvas.width !== nextWidth || canvas.height !== nextHeight) {
            canvas.width = nextWidth;
            canvas.height = nextHeight;
        }

        ctx.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
    }

    private getCssVarValue(variableName: string, fallbackColor: string): string {
        const cssValue = getComputedStyle(document.documentElement).getPropertyValue(variableName).trim();
        return cssValue || fallbackColor;
    }

    private getCurveColorMap(): CurveColors {
        return {
            IN: this.getCssVarValue('--fade-preview-in', '#198754'),
            OUT: this.getCssVarValue('--fade-preview-out', '#dc3545'),
            AXIS: this.getCssVarValue('--fade-preview-axis', '#ced4da'),
            BG: this.getCssVarValue('--fade-preview-bg', '#f8f9fa'),
            MUTED: this.getCssVarValue('--fade-preview-off', '#6c757d'),
        };
    }

    private parseDefaultFadesByType(typeSelect: HTMLSelectElement): Record<string, DefaultFadeConfig> {
        const rawMetadata = typeSelect.dataset.defaultFades;
        if (!rawMetadata) {
            return {};
        }

        try {
            const parsed = JSON.parse(rawMetadata) as Record<string, DefaultFadeConfig>;
            if (parsed && typeof parsed === 'object') {
                return parsed;
            }
        } catch (error) {
            ConsoleCustom.error('Impossible de parser data-default-fades', error);
        }
        return {};
    }

    private resolveFadeValue(
        selectedFadeValue: string,
        playlistType: string,
        defaultFadesByType: Record<string, DefaultFadeConfig>,
        fieldName: 'fadeIn' | 'fadeOut',
    ): string {
        if (selectedFadeValue !== 'DEFAULT') {
            return selectedFadeValue;
        }

        const playlistDefaults = defaultFadesByType[playlistType];
        const fallbackValue = fieldName === 'fadeIn' ? 'EASE' : 'EASE';
        return playlistDefaults?.[fieldName] || fallbackValue;
    }

    private normalizeFadeValue(rawFadeValue: string): string {
        if (!rawFadeValue) {
            return 'disabled';
        }

        const trimmedValue = rawFadeValue.trim();
        const mappedStrategy = FADE_ENUM_TO_STRATEGY[trimmedValue];
        if (mappedStrategy) {
            return mappedStrategy;
        }

        return trimmedValue.toLowerCase();
    }

    private drawCurve(
        ctx: CanvasRenderingContext2D,
        strategy: FadeStrategy,
        color: string,
        startVolume: number,
        endVolume: number,
        padding: number,
        drawWidth: number,
        drawHeight: number,
        canvasHeight: number,
        lineWidth: number,
    ): void {
        const STEPS = 100;
        ctx.strokeStyle = color;
        ctx.lineWidth = lineWidth;
        ctx.globalAlpha = 1;
        ctx.beginPath();

        for (let i = 0; i <= STEPS; i++) {
            const progress = i / STEPS;
            const volume = strategy.calculateVolume(startVolume, endVolume, progress);
            const x = padding + progress * drawWidth;
            const y = canvasHeight - padding - volume * drawHeight;
            if (i === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        }

        ctx.stroke();
    }

    private drawOffLine(
        ctx: CanvasRenderingContext2D,
        color: string,
        padding: number,
        canvasWidth: number,
        canvasHeight: number,
        lineWidth: number,
    ): void {
        ctx.strokeStyle = color;
        ctx.lineWidth = lineWidth;
        ctx.globalAlpha = 1;
        ctx.beginPath();
        ctx.moveTo(padding, canvasHeight - padding);
        ctx.lineTo(canvasWidth - padding, canvasHeight - padding);
        ctx.stroke();
    }

    private renderMergedFadeLegend(
        legendEl: HTMLElement,
        fadeInLabel: string,
        fadeOutLabel: string,
        colors: CurveColors,
    ): void {
        legendEl.innerHTML = `
            <span class="fade-preview-legend__item is-active fade-preview-legend__item--in">
                <span class="fade-preview-legend__swatch" style="--fade-color:${colors.IN}"></span>
                Fade in: ${fadeInLabel}
            </span>
            <span class="fade-preview-legend__item is-active fade-preview-legend__item--out">
                <span class="fade-preview-legend__swatch" style="--fade-color:${colors.OUT}"></span>
                Fade out: ${fadeOutLabel}
            </span>
        `;
    }
}