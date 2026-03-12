import os
import json
import uuid
import logging
import threading

from flask import Flask, render_template, request, Response, jsonify, send_from_directory
from flask_cors import CORS

from dual_agent import DualAgentSystem, fetch_models, fetch_balance

app = Flask(__name__)
CORS(app)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

HEARTBEAT_INTERVAL = 15
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)

def _sse(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"

def generate_events(task, key, model1, model2, params, retries, stop_event):
    collected = []

    def event_callback(event_type, data):
        collected.append((event_type, data))

    agent = DualAgentSystem(
        key=key,
        model1=model1,
        model2=model2,
        retries=retries,
        params=params,
    )

    result_holder = {"error": None}

    def run_agent():
        try:
            agent.run(task, event_callback=event_callback)
        except Exception as e:
            logger.exception("Agent run error")
            result_holder["error"] = str(e)

    thread = threading.Thread(target=run_agent, daemon=True)
    thread.start()

    yield _sse({"event": "connected", "message": "Task started."})

    import time
    last_heartbeat = time.time()
    last_sent = 0

    while thread.is_alive() or last_sent < len(collected):
        if stop_event.is_set():
            logger.info("Client disconnected — stopping stream.")
            break

        now = time.time()

        while last_sent < len(collected):
            event_type, data = collected[last_sent]
            last_sent += 1
            payload = {**data, "event": event_type}
            logger.debug("SSE emit: %s", event_type)
            yield _sse(payload)
            last_heartbeat = time.time()

        if now - last_heartbeat >= HEARTBEAT_INTERVAL:
            yield _sse({"event": "heartbeat"})
            last_heartbeat = now

        time.sleep(0.05)

    if result_holder["error"]:
        yield _sse({"event": "error", "message": result_holder["error"]})

    yield _sse({"event": "stream_end"})

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/status")
def status():
    return {"status": "online", "service": "DuOgent API"}

@app.route("/api/models", methods=["POST"])
def get_models():
    data = request.get_json(silent=True) or {}
    key = data.get("key", "").strip()
    if not key:
        return jsonify({"error": "Key required"}), 400
    models = fetch_models(key)
    return jsonify({"models": models})

@app.route("/api/balance", methods=["POST"])
def get_balance():
    data = request.get_json(silent=True) or {}
    key = data.get("key", "").strip()
    result = {}
    if key:
        result["balance"] = fetch_balance(key)
    return jsonify(result)

@app.route("/api/save", methods=["POST"])
def save_output():
    """Save generated HTML to /static and return the URL path."""
    data = request.get_json(silent=True) or {}
    html = data.get("html", "").strip()
    filename = data.get("filename", "").strip()
    if not html:
        return jsonify({"error": "No HTML provided"}), 400
    if not filename or not filename.endswith(".html"):
        filename = f"output-{uuid.uuid4().hex[:8]}.html"
    safe = "".join(c for c in filename if c.isalnum() or c in "-_.").lower()
    if not safe.endswith(".html"):
        safe += ".html"
    filepath = os.path.join(STATIC_DIR, safe)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    return jsonify({"url": f"/static/{safe}", "filename": safe})

@app.route("/api/run", methods=["GET", "POST"])
def run_task():
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
    else:
        data = request.args.to_dict()

    task = data.get("task", "").strip()
    key = data.get("key", "").strip()
    model1 = data.get("model1", "gemini-fast").strip()
    model2 = data.get("model2", "gemini-fast").strip()
    retries = int(data.get("retries", 3))

    params = {}
    enabled = data.get("enabled_params", {})
    if enabled.get("temperature"):
        params["temperature"] = float(data.get("temperature", 0.7))
    if enabled.get("top_p"):
        params["top_p"] = float(data.get("top_p", 0.95))
    if enabled.get("presence_penalty"):
        params["presence_penalty"] = float(data.get("presence_penalty", 0.1))
    if enabled.get("frequency_penalty"):
        params["frequency_penalty"] = float(data.get("frequency_penalty", 0.1))

    if not task:
        return {"error": "Task is required."}, 400
    if not key:
        return {"error": "API key is required."}, 400

    stop_event = threading.Event()

    resp = Response(
        generate_events(task, key, model1, model2, params, retries, stop_event),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

    resp.call_on_close(stop_event.set)
    return resp

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
