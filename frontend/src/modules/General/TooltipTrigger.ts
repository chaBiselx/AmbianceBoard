import * as bootstrap from 'bootstrap';
import ConsoleCustom from '@/modules/General/ConsoleCustom';
import Time from '@/modules/Util/Time';

class TooltipTrigger {
    private static clickHandlerAttached = false;
    private readonly hideTimers = new Map<HTMLElement, ReturnType<typeof setTimeout>>();

    public addEventListener(): void {
        if (TooltipTrigger.clickHandlerAttached) {
            return;
        }

        TooltipTrigger.clickHandlerAttached = true;

        document.addEventListener('click', (event) => {
            if (!(event.target instanceof Element)) {
                return;
            }

            const trigger = event.target.closest<HTMLElement>('.js-tooltip-trigger[data-tooltip-target]');
            const targetId = trigger?.dataset.tooltipTarget;

            if (!trigger || !targetId) {
                return;
            }

            const tooltipTarget = document.getElementById(targetId);
            if (!tooltipTarget) {
                ConsoleCustom.warn(`Tooltip trigger target not found: ${targetId}`);
                return;
            }

            // creation
            bootstrap.Tooltip.getOrCreateInstance(tooltipTarget).show();
            const previousTimer = this.hideTimers.get(tooltipTarget);
            if (previousTimer) {
                clearTimeout(previousTimer);
            }

            // remove
            const timer = setTimeout(() => {
                bootstrap.Tooltip.getOrCreateInstance(tooltipTarget).hide();
                this.hideTimers.delete(tooltipTarget);
            }, Time.get_seconds(5));
            this.hideTimers.set(tooltipTarget, timer);
        });
    }
}

export default TooltipTrigger;
