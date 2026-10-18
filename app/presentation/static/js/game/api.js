export class ApiClient {
  async #request(path, method = "GET", body = null) {
    const response = await fetch(path, {
      method,
      headers: { "Content-Type": "application/json" },
      body: body === null ? undefined : JSON.stringify(body),
    });
    if (!response.ok) {
      const detail = await response.json().catch(() => ({}));
      const error = new Error(detail.error || `HTTP ${response.status} en ${path}`);
      error.status = response.status;
      throw error;
    }
    return response.status === 204 ? null : response.json();
  }

  startSession(patientId, activityId, calibrationId) {
    return this.#request("/sessions", "POST", {
      patient_id: patientId, activity_id: activityId, calibration_id: calibrationId,
    });
  }

  pushReading(sessionId, samples, sampleRateHz) {
    return this.#request(`/sessions/${sessionId}/readings`, "POST",
      { samples, sample_rate_hz: sampleRateHz });
  }

  liveState(sessionId) {
    return this.#request(`/sessions/${sessionId}/live`);
  }

  closeSession(sessionId) {
    return this.#request(`/sessions/${sessionId}/close`, "POST", {});
  }

  startCalibration(patientId) {
    return this.#request(`/patients/${patientId}/calibration-runs`, "POST", {});
  }

  calibrationStatus(runId) {
    return this.#request(`/calibration-runs/${runId}`);
  }

  setCalibrationPhase(runId, phase) {
    return this.#request(`/calibration-runs/${runId}/phase`, "POST", { phase });
  }

  pushCalibrationReading(runId, samples, sampleRateHz) {
    return this.#request(`/calibration-runs/${runId}/readings`, "POST",
      { samples, sample_rate_hz: sampleRateHz });
  }

  finishCalibration(runId, label) {
    return this.#request(`/calibration-runs/${runId}/finish`, "POST", { label });
  }

  cancelCalibration(runId) {
    return this.#request(`/calibration-runs/${runId}`, "DELETE");
  }
}