export const GROUND_Y = 200;

export class Dino {
  static WIDTH = 30;
  static HEIGHT = 40;
  static JUMP_SPEED = 600;   // px/s
  static GRAVITY = 1500;     // px/s²  → salto de ~120 px y ~0.8 s en el aire

  constructor(x) {
    this.x = x;
    this.reset();
  }

  reset() {
    this.height = 0;     // altura sobre el suelo
    this.velocity = 0;
  }

  get onGround() {
    return this.height === 0;
  }

  jump() {
    if (this.onGround) this.velocity = Dino.JUMP_SPEED;
  }

  update(dt) {
    if (this.onGround && this.velocity === 0) return;
    this.velocity -= Dino.GRAVITY * dt;
    this.height = Math.max(0, this.height + this.velocity * dt);
    if (this.height === 0) this.velocity = 0;
  }

  get top() {
    return GROUND_Y - this.height - Dino.HEIGHT;
  }

  /** Caja de colisión algo más pequeña que el dibujo, para ser indulgente. */
  get box() {
    return { x: this.x + 4, y: this.top + 4, w: Dino.WIDTH - 8, h: Dino.HEIGHT - 8 };
  }
}

export class Obstacle {
  constructor(x, width, height) {
    this.x = x;
    this.width = width;
    this.height = height;
  }

  get box() {
    return { x: this.x, y: GROUND_Y - this.height, w: this.width, h: this.height };
  }
}

export class ObstacleField {
  static MIN_GAP = 400;   // px entre obstáculos: tiempo para relajar y volver a contraer
  static MAX_GAP = 650;

  items = [];
  #gap = 0;

  constructor(canvasWidth) {
    this.canvasWidth = canvasWidth;
  }

  reset() {
    this.items = [];
    this.#gap = 0;
  }

  update(dt, speed) {
    for (const obstacle of this.items) obstacle.x -= speed * dt;
    this.items = this.items.filter((o) => o.x + o.width > 0);

    const last = this.items[this.items.length - 1];
    if (!last || last.x < this.canvasWidth - this.#gap) {
      const width = 16 + Math.random() * 10;
      const height = 30 + Math.random() * 20;
      this.items.push(new Obstacle(this.canvasWidth, width, height));
      this.#gap = ObstacleField.MIN_GAP
        + Math.random() * (ObstacleField.MAX_GAP - ObstacleField.MIN_GAP);
    }
  }
}