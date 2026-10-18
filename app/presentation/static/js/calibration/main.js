import { ApiClient } from "../game/api.js";
import { buildProtocol } from "./protocol.js";
import { ProtocolRunner } from "./runner.js";
import { SimulatedCalibrationSignal } from "./simulator.js";

const $ = (id) => document.getElementById(id);
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const STATUS_POLL_MS = 150;
const DEVICE_WAIT_MS = 60000;

class CalibrationApp {
  #runId = null;
  #runner = null;
  #signal = null;
  #poller = null;
  #cancelled = false;
  #peak = 1;

  constructor() {
    this.api = new ApiClient();
    this.patientId = Number($("calibration-root").dataset.patientId);
    $("start").addEventListener("click", () => this.start());
    $("cancel").addEventListener("click", () => this.cancel());
  }

  async start() {
    if (!$("label").value.trim()) {
      this.#setStatus("Escribe qué músculo vas a calibrar.");
      return;
    }
    this.#cancelled = false;
    this.#peak = 1;
    $("result").hidden = true;
    this.#setRunning(true);

    try {
      const run = await this.api.startCalibration(this.patientId);
      this.#runId = run.run_id;
      this.#startPolling();

      if ($("mode").value === "simulator") {
        this.#signal = new SimulatedCalibrationSignal(this.api, this.#runId);
        this.#signal.start();
        this.#setStatus("Simulador: mantén ESPACIO mientras se pida contraer.");
      } else {
        this.#setStatus("Mantén pulsado BOOT 2 segundos en el ESP32 y suéltalo para conectarlo…");
        await this.#waitForDevice();
      }
      await this.#runProtocol();
    } catch (error) {
      this.#setStatus(`Calibración interrumpida: ${error.message}`);
      await this.#teardown(true);
    }
  }

  cancel() {
    this.#cancelled = true;
    this.#runner?.cancel();
  }

  async #waitForDevice() {
    const deadline = performance.now() + DEVICE_WAIT_MS;
    while (performance.now() < deadline) {
      if (this.#cancelled) throw new Error("cancelada");
      const status = await this.api.calibrationStatus(this.#runId);
      if (status.total_windows > 0) return;
      await sleep(300);
    }
    throw new Error("el dispositivo no se conectó a tiempo");
  }

  async #runProtocol() {
    this.#runner = new ProtocolRunner(this.api, this.#runId, buildProtocol(),
                                      (tick) => this.#renderStep(tick));
    $("instruction").hidden = false;
    this.#setStatus("");
    const completed = await this.#runner.run();
    if (!completed) {
      this.#setStatus("Calibración cancelada.");
      return this.#teardown(true);
    }
    await this.#finish();
  }

  async #finish() {
    this.#setStatus("Calculando la calibración…");
    try {
      const profile = await this.api.finishCalibration(this.#runId, $("label").value.trim());
      this.#runId = null;               // el servidor ya eliminó la corrida
      this.#showResult(profile);
      this.#setStatus("");
      await this.#teardown(false);
    } catch (error) {
      this.#setStatus(`No se pudo calibrar: ${error.message}. Revisa los electrodos y repite.`);
      await this.#teardown(true);
    }
  }

  async #teardown(deleteRun) {
    this.#signal?.stop();
    this.#signal = null;
    clearInterval(this.#poller);
    this.#runner = null;
    if (deleteRun && this.#runId !== null) {
      await this.api.cancelCalibration(this.#runId).catch(() => {});   // puede no existir ya
    }
    this.#runId = null;
    $("instruction").hidden = true;
    this.#setRunning(false);
  }

  #startPolling() {
    this.#poller = setInterval(async () => {
      if (this.#runId === null) return;
      try {
        this.#renderSignal(await this.api.calibrationStatus(this.#runId));
      } catch (error) {
        // 404 al cerrar la corrida: es normal, se ignora
      }
    }, STATUS_POLL_MS);
  }

  #renderStep({ index, total, step, remaining }) {
    $("instruction-text").textContent = step.text;
    $("instruction-timer").textContent = `${Math.ceil(remaining)} s`;
    const done = index + 1 - remaining / step.seconds;
    $("protocol-fill").style.width = `${Math.round((done / total) * 100)}%`;
  }

  #renderSignal({ last_amplitude: amplitude }) {
    this.#peak = Math.max(this.#peak, amplitude);
    $("signal-text").textContent = `Amplitud: ${Math.round(amplitude)} mV`;
    $("signal-fill").style.width = `${Math.round((amplitude / this.#peak) * 100)}%`;
  }

  #showResult(profile) {
    $("res-rest").textContent = Math.round(profile.rest_amplitude);
    $("res-max").textContent = Math.round(profile.max_amplitude);
    $("res-freq").textContent = Math.round(profile.base_frequency);
    $("result").hidden = false;
  }

  #setRunning(running) {
    $("start").disabled = running;
    $("cancel").disabled = !running;
    $("mode").disabled = running;
    $("label").disabled = running;
  }

  #setStatus(text) {
    $("status").textContent = text;
  }
}

new CalibrationApp();