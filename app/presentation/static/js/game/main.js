import { ApiClient } from "./api.js";
import { DeviceEmgInput, SimulatedEmgInput, WebSocketDeviceInput } from "./inputs.js";
import { GAMES } from "./registry.js";

const $ = (id) => document.getElementById(id);
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const DEVICE_WAIT_MS = 60000;

class GameApp {
  #sessionId = null;
  #input = null;
  #game = null;
  #aborted = false;

  constructor() {
    this.api = new ApiClient();
    const root = $("game-root");
    this.patientId = Number(root.dataset.patientId);
    this.activityId = Number(root.dataset.activityId);
    this.threshold = Number(root.dataset.threshold);
    this.GameClass = GAMES[root.dataset.game];
    this.canvas = $("canvas");

    $("hud-progress-label").textContent = this.GameClass.label;
    $("start").addEventListener("click", () => this.start());
    $("stop").addEventListener("click", () => this.finish("Juego terminado."));
  }

  async start() {
    this.#aborted = false;
    this.#setRunning(true);
    this.#setStatus("Iniciando…");
    try {
      const session = await this.api.startSession(
        this.patientId, this.activityId, Number($("calibration").value));
      this.#sessionId = session.id;
      this.#input = this.#createInput();
      this.#input.start(this.#sessionId);

      if ($("mode").value === "device" && !(await this.#waitForDevice())) return;

      this.#game = new this.GameClass(this.canvas, this.#input, {
        threshold: this.threshold,
        onFrame: (state) => this.#renderHud(state),
        onGameOver: () => this.finish("Fin de la partida."),
      });
      this.#game.start();
      this.#setStatus(`Sesión ${this.#sessionId} en curso. ¡Contrae el músculo!`);
    } catch (error) {
      this.#setStatus(`No se pudo iniciar: ${error.message}`);
      this.#setRunning(false);
    }
  }

  async finish(reason) {
    if (this.#sessionId === null) return;
    this.#aborted = true;
    this.#game?.stop();
    this.#input?.stop();

    let score = this.#input?.score ?? 0;
    try {
      score = (await this.api.closeSession(this.#sessionId)).score;
    } catch (error) {
      console.warn("No se pudo cerrar la sesión", error);
    }
    const progress = Math.floor(this.#game?.progress ?? 0);
    this.#setStatus(`${reason} Puntaje de rehabilitación: ${score} · ${this.GameClass.label}: ${progress}`);
    $("hud-score").textContent = score;
    this.#sessionId = null;
    this.#game = null;
    this.#setRunning(false);
  }

  async #waitForDevice() {
    this.#setStatus(`Sesión ${this.#sessionId} creada. Pulsa BOOT en el ESP32 para unirte…`);
    const deadline = performance.now() + DEVICE_WAIT_MS;
    while (!this.#aborted && performance.now() < deadline) {
      try {
        await this.api.liveState(this.#sessionId);
        return true;
      } catch (error) {
        if (error.status !== 404) throw error;     // 404 = aún sin lecturas
      }
      await sleep(300);
    }
    if (!this.#aborted) await this.finish("El dispositivo no se conectó.");
    return false;
  }

  #createInput() {
    if ($("mode").value === "device") return new WebSocketDeviceInput();
    const option = $("calibration").selectedOptions[0];
    const calibration = { rest: Number(option.dataset.rest), max: Number(option.dataset.max) };
    return new SimulatedEmgInput(this.api, calibration, this.canvas);
  }

  #renderHud({ progress, activation, score }) {
    $("hud-progress").textContent = Math.floor(progress);
    $("hud-score").textContent = score;
    $("activation-fill").style.width = `${Math.round(activation * 100)}%`;
  }

  #setRunning(running) {
    $("start").disabled = running;
    $("stop").disabled = !running;
    $("mode").disabled = running;
    $("calibration").disabled = running;
  }

  #setStatus(text) {
    $("status").textContent = text;
  }
}

new GameApp();