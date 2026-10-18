const DURATION_S = 60;
const BAND_HALF_WIDTH = 0.12;   // tolerancia en unidades de activación
const CENTER = 0.6;
const SWING = 0.25;
const PERIOD_S = 8;

export class TrackerGame {
  static label = "Tiempo en la franja (s)";

  #running = false;
  #frameId = null;
  #lastTime = 0;
  #elapsed = 0;
  #inBand = 0;

  constructor(canvas, input, { onFrame, onGameOver }) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");
    this.input = input;
    this.onFrame = onFrame;
    this.onGameOver = onGameOver;
  }

  get progress() {
    return this.#inBand;
  }

  start() {
    this.#elapsed = 0;
    this.#inBand = 0;
    this.#running = true;
    this.#lastTime = performance.now();
    this.#frameId = requestAnimationFrame((t) => this.#frame(t));
  }

  stop() {
    this.#running = false;
    cancelAnimationFrame(this.#frameId);
  }

  #target() {
    return CENTER + SWING * Math.sin((2 * Math.PI * this.#elapsed) / PERIOD_S);
  }

  #frame(now) {
    if (!this.#running) return;
    const dt = Math.min((now - this.#lastTime) / 1000, 0.05);
    this.#lastTime = now;
    this.#elapsed += dt;

    const target = this.#target();
    const activation = this.input.activation;
    if (Math.abs(activation - target) <= BAND_HALF_WIDTH) this.#inBand += dt;

    this.#draw(target, activation);
    this.onFrame({ progress: this.#inBand, activation, score: this.input.score });

    if (this.#elapsed >= DURATION_S) {
      this.stop();
      this.onGameOver({ progress: this.#inBand });
      return;
    }
    this.#frameId = requestAnimationFrame((t) => this.#frame(t));
  }

  #draw(target, activation) {
    const { ctx, canvas } = this;
    const y = (level) => canvas.height * (1 - level);   // 0 abajo, 1 arriba
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = getComputedStyle(canvas).color;

    ctx.globalAlpha = 0.2;
    ctx.fillRect(0, y(target + BAND_HALF_WIDTH), canvas.width,
                 canvas.height * 2 * BAND_HALF_WIDTH);
    ctx.globalAlpha = 1;

    ctx.beginPath();
    ctx.arc(canvas.width / 2, y(activation), 12, 0, 2 * Math.PI);
    ctx.fill();

    ctx.fillRect(0, 0, canvas.width * (1 - this.#elapsed / DURATION_S), 4);   // tiempo restante
  }
}