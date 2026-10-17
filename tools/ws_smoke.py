import json
import math
import time

from simple_websocket import Client

SESSION_ID = 1   # una sesión abierta (POST /sessions)
ws = Client.connect(f"ws://127.0.0.1:5000/ws/sessions/{SESSION_ID}/device")

samples = [60 * math.sin(2 * math.pi * 50 * i / 1000) for i in range(100)]
message = json.dumps({"samples": samples, "sample_rate_hz": 1000})

for _ in range(10):
    start = time.perf_counter()
    ws.send(message)
    reply = json.loads(ws.receive(timeout=2))
    print(f"{(time.perf_counter() - start) * 1000:5.1f} ms  {reply}")