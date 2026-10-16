import { ApiClient } from "./api.js";
import { Game } from "./game.js";
import { DeviceEmgInput, SimulatedEmgInput } from "./inputs.js";

const $ = (id) => document.getElementById(id);

class GameApp {
  #sessionId = null;
  #input = null;
  #game = null;

  constructor() {
    this.api = new ApiClient();
    const root = $("game-root");
    this.patientId = Number(root.dataset.patientId);
    this.threshold = Number(root.dataset.threshold);
    this.canvas = $("canvas");

    $("start").addEventListener("click", () => this.start());
    $("stop").addEventListener("click", () => this.finish());
    $("mode").addEventListener("change", () => this.#syncControls());
    this.#syncControls();
  }

  async start() {
    this.#setRunning(true);
    this.#setStatus("Iniciando…");
    try {
      this.#sessionId = await this.#resolveSession();
      this.#input = this.#createInput();
      this.#input.start(this.#sessionId);

      this.#game = new Game(this.canvas, this.#input, {
        threshold: this.threshold,
        onFrame: (state) => this.#renderHud(state),
        onGameOver: () => this.finish("Chocaste con un obstáculo."),
      });
      this.#game.start();
      this.#setStatus(`Sesión ${this.#sessionId} en curso. ¡Contrae para saltar!`);
    } catch (error) {
      this.#setStatus(`No se pudo iniciar: ${error.message}`);
      this.#setRunning(false);
    }
  }

  async finish(reason = "Juego terminado.") {
    if (this.#sessionId === null) return;
    this.#game.stop();
    this.#input.stop();

    let score = this.#input.score;
    try {
      score = (await this.api.closeSession(this.#sessionId)).score;
    } catch (error) {
      console.warn("No se pudo cerrar la sesión", error);
    }
    this.#setStatus(
      `${reason} Puntaje de rehabilitación: ${score} · Distancia: ${Math.floor(this.#game.distance)} m`);
    $("hud-score").textContent = score;
    this.#sessionId = null;
    this.#setRunning(false);
  }

  async #resolveSession() {
    if ($("mode").value === "simulator") {
      const session = await this.api.startSession(
        this.patientId, Number($("activity").value), Number($("calibration").value));
      return session.id;
    }
    // Modo dispositivo: la sesión la abrió el ESP32 con el botón BOOT
    const sessions = await this.api.patientSessions(this.patientId);
    const open = sessions.filter((s) => s.ended_at === null);
    if (open.length === 0) throw new Error("no hay sesión abierta; pulsa BOOT en el ESP32");
    return open[open.length - 1].id;
  }

  #createInput() {
    if ($("mode").value === "device") return new DeviceEmgInput(this.api);
    const option = $("calibration").selectedOptions[0];
    const calibration = { rest: Number(option.dataset.rest), max: Number(option.dataset.max) };
    return new SimulatedEmgInput(this.api, calibration, this.canvas);
  }

  #renderHud({ distance, activation, score }) {
    $("hud-distance").textContent = Math.floor(distance);
    $("hud-score").textContent = score;
    $("activation-fill").style.width = `${Math.round(activation * 100)}%`;
  }

  #syncControls() {
    const isDevice = $("mode").value === "device";
    $("activity").disabled = isDevice;
    $("calibration").disabled = isDevice;
  }

  #setRunning(running) {
    $("start").disabled = running;
    $("stop").disabled = !running;
    $("mode").disabled = running;
  }

  #setStatus(text) {
    $("status").textContent = text;
  }
}

new GameApp();