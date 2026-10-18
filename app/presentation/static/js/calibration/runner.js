const TICK_MS = 100;
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

export class ProtocolRunner {
  #cancelled = false;

  constructor(api, runId, steps, onTick) {
    this.api = api;
    this.runId = runId;
    this.steps = steps;
    this.onTick = onTick;
  }

  cancel() {
    this.#cancelled = true;
  }

  /** Devuelve true si el protocolo terminó, false si se canceló. */
  async run() {
    for (const [index, step] of this.steps.entries()) {
      if (this.#cancelled) return false;
      await this.api.setCalibrationPhase(this.runId, step.phase);
      const end = performance.now() + step.seconds * 1000;
      while (performance.now() < end) {
        if (this.#cancelled) return false;
        this.onTick({ index, total: this.steps.length, step,
                      remaining: (end - performance.now()) / 1000 });
        await sleep(TICK_MS);
      }
    }
    return true;
  }
}