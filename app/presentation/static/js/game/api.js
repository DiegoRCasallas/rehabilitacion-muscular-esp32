export class ApiClient {
  async #request(path, method = "GET", body = null) {
    const response = await fetch(path, {
      method,
      headers: { "Content-Type": "application/json" },
      body: body === null ? undefined : JSON.stringify(body),
    });
    if (!response.ok) {
      const error = new Error(`HTTP ${response.status} en ${path}`);
      error.status = response.status;
      throw error;
    }
    return response.json();
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

  patientSessions(patientId) {
    return this.#request(`/patients/${patientId}/sessions`);
  }
}