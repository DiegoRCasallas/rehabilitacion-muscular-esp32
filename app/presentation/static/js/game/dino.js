import { Dino, GROUND_Y, ObstacleField } from "./entities.js";

const BASE_SPEED = 160;   // px/s: lento a propósito, hay latencia entre contracción y salto
const MAX_SPEED = 240;
const ACCELERATION = 2;   // px/s por segundo

function overlaps(a, b) {
  return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
}

export class DinoGame {
  #running = false;
  #lastTime = 0;
  #frameId = null;
  #wasActive = false;
  #speed = BASE_SPEED;
  #distance = 0;
  static label = "Distancia (m)";

  constructor(canvas, input, { threshold, onFrame, onGameOver }) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");
    this.input = input;
    this.threshold = threshold;
    this.onFrame = onFrame;
    this.onGameOver = onGameOver;
    this.dino = new Dino(60);
    this.field = new ObstacleField(canvas.width);
  }

  get distance() {
    return this.#distance;
  }

    get progress() {
    return this.#distance;
  }

  start() {
    this.dino.reset();
    this.field.reset();
    this.#speed = BASE_SPEED;
    this.#distance = 0;
    this.#wasActive = false;
    this.#running = true;
    this.#lastTime = performance.now();
    this.#frameId = requestAnimationFrame((t) => this.#frame(t));
  }

  stop() {
    this.#running = false;
    cancelAnimationFrame(this.#frameId);
  }

  #frame(now) {
    if (!this.#running) return;
    const dt = Math.min((now - this.#lastTime) / 1000, 0.05);
    this.#lastTime = now;

    this.#update(dt);
    this.#draw();
    if (this.#running) this.#frameId = requestAnimationFrame((t) => this.#frame(t));
  }

  #update(dt) {
    const active = this.input.activation >= this.threshold;
    if (active && !this.#wasActive) this.dino.jump();   // salta al cruzar el umbral
    this.#wasActive = active;

    this.#speed = Math.min(MAX_SPEED, this.#speed + ACCELERATION * dt);
    this.dino.update(dt);
    this.field.update(dt, this.#speed);
    this.#distance += (this.#speed * dt) / 10;

    this.onFrame({
      progress: this.#distance,
      activation: this.input.activation,
      score: this.input.score,
    });

    if (this.field.items.some((o) => overlaps(this.dino.box, o.box))) {
      this.stop();
      this.onGameOver({ progress: this.#distance });
    }
  }

  #draw() {
    const { ctx, canvas } = this;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = getComputedStyle(canvas).color;

    ctx.fillRect(0, GROUND_Y, canvas.width, 2);
    for (const o of this.field.items) ctx.fillRect(o.x, GROUND_Y - o.height, o.width, o.height);

    const { x, top } = this.dino;
    ctx.fillRect(x, top + 12, 24, 28);        // cuerpo
    ctx.fillRect(x + 10, top, 20, 16);        // cabeza
    ctx.clearRect(x + 24, top + 4, 3, 3);     // ojo
  }
}