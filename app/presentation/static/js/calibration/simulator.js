const SAMPLE_RATE_HZ = 1000;
const WINDOW_SIZE = 200;
const INTERVAL_MS = 200;
const FREQUENCY_HZ = 50;
const REST_PEAK_TO_PEAK = 60;          // mV
const CONTRACTION_PEAK_TO_PEAK = 800;  // mV

/** Genera ventanas sintéticas: reposo, o contracción mientras se mantiene ESPACIO. */
export class SimulatedCalibrationSignal {
  #timer = null;
  #holding = false;
  #busy = false;
  #onKeyDown = (e) => { if (e.code === "Space") { e.preventDefault(); this.#holding = true; } };
  #onKeyUp = (e) => { if (e.code === "Space") { e.preventDefault(); this.#holding = false; } };

  constructor(api, runId) {
    this.api = api;
    this.runId = runId;
  }

  start() {
    window.addEventListener("keydown", this.#onKeyDown);
    window.addEventListener("keyup", this.#onKeyUp);
    this.#timer = setInterval(() => this.#push(), INTERVAL_MS);
  }

  stop() {
    clearInterval(this.#timer);
    window.removeEventListener("keydown", this.#onKeyDown);
    window.removeEventListener("keyup", this.#onKeyUp);
  }

  async #push() {
    if (this.#busy) return;
    this.#busy = true;
    try {
      const base = this.#holding ? CONTRACTION_PEAK_TO_PEAK : REST_PEAK_TO_PEAK;
      const peakToPeak = base * (1 + (Math.random() - 0.5) * 0.2);   // ±10 % de ruido
      const amplitude = peakToPeak / 2;
      const samples = Array.from({ length: WINDOW_SIZE }, (_, i) =>
        amplitude * Math.sin(2 * Math.PI * FREQUENCY_HZ * i / SAMPLE_RATE_HZ));
      await this.api.pushCalibrationReading(this.runId, samples, SAMPLE_RATE_HZ);
    } catch (error) {
      console.warn(error);
    } finally {
      this.#busy = false;
    }
  }
}