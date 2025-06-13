type TriggerFn = (defaultStrategy?: string) => void;
let trigger: TriggerFn | null = null;

export function setLabelPrintTrigger(fn: TriggerFn) {
  trigger = fn;
}

export function openLabelPrintDialog(defaultStrategy?: string) {
  trigger?.(defaultStrategy);
}
