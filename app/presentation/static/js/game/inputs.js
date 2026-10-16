const SAMPLE_RATE_HZ = 1000;
const WINDOW_SIZE = 200;
const WINDOW_INTERVAL_MS = 200;
const SIMULATED_FREQUENCY_HZ = 50;   // 20 muestras por ciclo: el pico cae en una muestra
const SIMULATED_EFFORT = 0.8;        // fracción del rango de calibración al "contraer"
const DEVICE_POLL_MS = 150;

class PollingInput {
  activation = 0;
  score = 0;
  sessionId = null;
  #timer = null;
  #busy = false;

  constructor(intervalMs) {
    this.intervalMs = intervalMs;
  }

  start(sessionId) {
    this.sessionId = sessionId;
    this.activation = 0;
    this.score = 0;
    this.#timer = setInterval(async () => {
      if (this.#busy) return;           // no solapar peticiones lentas
      this.#busy = true;
      try {
        await this.poll();
      } catch (error) {
        if (error.status !== 404) console.warn(error);   // 404 = aún sin lecturas
      } finally {
        this.#busy = false;
      }
    }, this.intervalMs);
  }

  stop() {
    clearInterval(this.#timer);
    this.#timer = null;
  }

  async poll() {
    throw new Error("poll() debe implementarse en la subclase");
  }
}

/** Genera ventanas sintéticas a partir del teclado o del toque en pantalla. */
export class SimulatedEmgInput extends PollingInput {
  #holding = false;
  #onKeyDown = (e) => { if (e.code === "Space") { e.preventDefault(); this.#holding = true; } };
  #onKeyUp = (e) => { if (e.code === "Space") { e.preventDefault(); this.#holding = false; } };
  #onPointerDown = () => { this.#holding = true; };
  #onPointerUp = () => { this.#holding = false; };

  constructor(api, calibration, pointerTarget) {
    super(WINDOW_INTERVAL_MS);
    this.api = api;
    this.calibration = calibration;   // { rest, max } en mV pico a pico
    this.pointerTarget = pointerTarget;
  }

  start(sessionId) {
    super.start(sessionId);
    window.addEventListener("keydown", this.#onKeyDown);
    window.addEventListener("keyup", this.#onKeyUp);
    this.pointerTarget.addEventListener("pointerdown", this.#onPointerDown);
    window.addEventListener("pointerup", this.#onPointerUp);
  }

  stop() {
    super.stop();
    this.#holding = false;
    window.removeEventListener("keydown", this.#onKeyDown);
    window.removeEventListener("keyup", this.#onKeyUp);
    this.pointerTarget.removeEventListener("pointerdown", this.#onPointerDown);
    window.removeEventListener("pointerup", this.#onPointerUp);
  }

  async poll() {
    const { rest, max } = this.calibration;
    const target = this.#holding ? rest + SIMULATED_EFFORT * (max - rest) : rest;
    const feedback = await this.api.pushReading(
      this.sessionId, this.#sineWave(target), SAMPLE_RATE_HZ);
    this.activation = feedback.activation;
    this.score = feedback.score;
  }

  #sineWave(peakToPeak) {
    const amplitude = peakToPeak / 2;
    return Array.from({ length: WINDOW_SIZE }, (_, i) =>
      amplitude * Math.sin(2 * Math.PI * SIMULATED_FREQUENCY_HZ * i / SAMPLE_RATE_HZ));
  }
}

/** Lee el estado en vivo que publica el ESP32. */
export class DeviceEmgInput extends PollingInput {
  constructor(api) {
    super(DEVICE_POLL_MS);
    this.api = api;
  }

  async poll() {
    const feedback = await this.api.liveState(this.sessionId);
    this.activation = feedback.activation;
    this.score = feedback.score;
  }
}