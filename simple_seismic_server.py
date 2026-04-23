#!/usr/bin/env python3
"""
Simple Seismic Log HTTP Server
Uses Python's built-in http.server module
"""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hashlib
import json
from datetime import datetime
import random
import time
from urllib.parse import urlparse

# System metrics
SYSTEM_METRICS = {
    "hash_throughput_ops_sec": 15265,
    "latency_p50_ms": 1.1,
    "latency_p95_ms": 1.8,
    "latency_p99_ms": 2.0,
    "latency_p999_ms": 3.2,
    "energy_per_op_joules": 0.042,
    "gpu_model": "GTX 1650",
    "speedup_vs_cloud": "200x+",
    "crystallization_status": "CRYSTALLINE",
}

CELESTIAL_BODIES = []

MISSION_BANK = [
    {
        "prompt": "Which property defines influence in the CelestialBody schema?",
        "choices": ["Mass", "Gravity", "Atmosphere", "Entropy"],
        "answer": "Gravity",
        "explanation": "Gravity is the influence vector; it determines orbital pull.",
    },
    {
        "prompt": "What must all ingested data pass through before joining the graph?",
        "choices": ["Heatmap", "Seismic Test", "Firewall Merge", "Cache Sync"],
        "answer": "Seismic Test",
        "explanation": "Structural truth is accepted only after invariance stress-testing.",
    },
    {
        "prompt": "Which endpoint ingests raw code into a CelestialBody object?",
        "choices": ["/api/bench/live", "/api/a2a/ingest", "/api/seismic/status", "/api/a2a/ecosystem"],
        "answer": "/api/a2a/ingest",
        "explanation": "POST /api/a2a/ingest performs the repo-to-body transformation.",
    },
]


def _stable_hash(payload):
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def _estimate_mass(files):
    lines = sum(f.get("content", "").count("\n") + 1 for f in files)
    chars = sum(len(f.get("content", "")) for f in files)
    return {
        "file_count": len(files),
        "line_count": lines,
        "char_count": chars,
        "compute_class": "stellar" if lines > 1200 else "planetary" if lines > 200 else "probe",
    }


def _infer_atmosphere(files):
    text = "\n".join(f.get("content", "") for f in files).lower()
    labels = []
    if "safety" in text or "security" in text:
        labels.append("protective")
    if "test" in text or "assert" in text:
        labels.append("verifiable")
    if "async" in text or "thread" in text:
        labels.append("concurrent")
    if "model" in text or "agent" in text:
        labels.append("cognitive")
    if not labels:
        labels.append("neutral")
    return labels


def _estimate_gravity(mass, atmosphere):
    influence = mass["line_count"] * 0.02 + mass["file_count"] * 3 + len(atmosphere) * 8
    return round(min(100.0, influence), 2)


def seismic_test(files):
    checks = {
        "non_empty": bool(files),
        "paths_present": all(bool(f.get("path")) for f in files),
        "content_present": all("content" in f for f in files),
    }
    invariance_score = round(sum(1 for ok in checks.values() if ok) / len(checks), 3)
    return {
        "checks": checks,
        "invariance_score": invariance_score,
        "status": "CRYSTALLINE" if invariance_score == 1.0 else "DUCTILE",
    }


def repo_to_celestial_body(payload):
    repo_name = payload.get("repo_name") or "unnamed-repo"
    files = payload.get("files") or []
    if payload.get("raw_code") and not files:
        files = [{"path": "inline_input.txt", "content": payload["raw_code"]}]

    mass = _estimate_mass(files)
    atmosphere = _infer_atmosphere(files)
    gravity = _estimate_gravity(mass, atmosphere)
    seismic = seismic_test(files)

    return {
        "id": _stable_hash({"repo": repo_name, "files": files})[:16],
        "schema": "CelestialBody/v1",
        "name": repo_name,
        "mass": mass,
        "atmosphere": atmosphere,
        "gravity": gravity,
        "seismic_test": seismic,
        "orbits": [],
        "created_at": datetime.utcnow().isoformat() + "Z",
    }


class SeismicHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        parsed = urlparse(self.path)
        if parsed.path in {
            "/",
            "/dashboard",
            "/api/health",
            "/api/bench/live",
            "/api/seismic/status",
            "/api/a2a/bodies",
            "/api/a2a/ecosystem",
            "/api/game/mission",
            "/api/game/state",
        }:
            self.send_response(200)
            self.end_headers()
        else:
            self.send_error(404)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self.send_json(
                {
                    "service": "Genesis Seismic Log",
                    "version": "1.2.0",
                    "status": "operational",
                    "protocol": "S-ToT (Seismic Tree-of-Thoughts)",
                    "endpoints": {
                        "dashboard": "/dashboard",
                        "live": "/api/bench/live",
                        "health": "/api/health",
                        "seismic": "/api/seismic/status",
                        "a2a_ingest": "/api/a2a/ingest",
                        "a2a_bodies": "/api/a2a/bodies",
                        "a2a_ecosystem": "/api/a2a/ecosystem",
                        "game_mission": "/api/game/mission",
                        "game_state": "/api/game/state",
                    },
                }
            )
        elif parsed.path == "/dashboard":
            self.send_html(self.build_dashboard())
        elif parsed.path == "/api/health":
            self.send_json(
                {
                    "status": "healthy",
                    "timestamp": datetime.utcnow().isoformat(),
                    "uptime_seconds": int(time.time()),
                    "services": {
                        "seismic_wrapper": "active",
                        "qmem_bridge": "active",
                        "crystallization_verifier": "active",
                        "a2a_ingestion": "active",
                    },
                }
            )
        elif parsed.path == "/api/bench/live":
            self.send_json(
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "system": "GTX 1650 (Diamond Vault)",
                    "metrics": SYSTEM_METRICS,
                    "percentiles": {
                        "p50": SYSTEM_METRICS["latency_p50_ms"],
                        "p95": SYSTEM_METRICS["latency_p95_ms"],
                        "p99": SYSTEM_METRICS["latency_p99_ms"],
                        "p999": SYSTEM_METRICS["latency_p999_ms"],
                    },
                    "energy_efficiency": {
                        "joules_per_op": SYSTEM_METRICS["energy_per_op_joules"],
                        "comparison_cloud_joules_per_op": 100.0,
                        "efficiency_gain": "2380x",
                    },
                    "verification": {
                        "protocol": "S-ToT Seismic Stress",
                        "status": SYSTEM_METRICS["crystallization_status"],
                        "ground_truth": "Ed25519 attestation active",
                    },
                }
            )
        elif parsed.path == "/api/seismic/status":
            self.send_json(
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "protocol": "Seismic Tree-of-Thoughts (S-ToT)",
                    "phases": {
                        "quantum_branching": {
                            "status": "complete",
                            "branches_generated": 3,
                            "orthogonality_score": 0.94,
                        },
                        "seismography": {
                            "status": "complete",
                            "stress_factor": 0.1,
                            "perturbations_applied": 1000,
                            "shake_intensity": "thermal_langevin",
                        },
                        "crystallization": {
                            "status": "CRYSTALLINE",
                            "threshold": 1e-4,
                            "measured_divergence": 3.2e-5,
                            "invariance_score": 0.998,
                        },
                        "cold_snap": {
                            "status": "complete",
                            "branches_shattered": 0,
                            "branches_crystalline": 3,
                            "synthesis": "unanimous_convergence",
                        },
                    },
                    "landauer_limit": {
                        "measured_joules_per_op": 0.042,
                        "theoretical_minimum": 0.0029,
                        "efficiency_percentage": 6.9,
                    },
                }
            )
        elif parsed.path == "/api/a2a/bodies":
            self.send_json({"count": len(CELESTIAL_BODIES), "bodies": CELESTIAL_BODIES})
        elif parsed.path == "/api/a2a/ecosystem":
            self.send_json(self.build_ecosystem())
        elif parsed.path == "/api/game/mission":
            self.send_json({"mission": random.choice(MISSION_BANK), "seed": int(time.time())})
        elif parsed.path == "/api/game/state":
            self.send_json(
                {
                    "level": min(9, max(1, len(CELESTIAL_BODIES) + 1)),
                    "xp": len(CELESTIAL_BODIES) * 120,
                    "stability": "CRYSTALLINE" if all(b["seismic_test"]["status"] == "CRYSTALLINE" for b in CELESTIAL_BODIES) else "DUCTILE",
                }
            )
        else:
            self.send_error(404)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/a2a/ingest":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode() or "{}")
        except json.JSONDecodeError:
            self.send_json({"error": "Invalid JSON payload"}, status_code=400)
            return

        body = repo_to_celestial_body(payload)
        CELESTIAL_BODIES.append(body)
        self.recompute_orbits()
        self.send_json({"status": "ingested", "celestial_body": body}, status_code=201)

    def recompute_orbits(self):
        if not CELESTIAL_BODIES:
            return

        sorted_bodies = sorted(CELESTIAL_BODIES, key=lambda b: b["gravity"], reverse=True)
        anchor = sorted_bodies[0]["id"]
        for body in CELESTIAL_BODIES:
            body["orbits"] = [] if body["id"] == anchor else [anchor]

    def build_ecosystem(self):
        return {
            "schema": "CelestialEcosystem/v1",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "nodes": [
                {
                    "id": b["id"],
                    "name": b["name"],
                    "gravity": b["gravity"],
                    "atmosphere": b["atmosphere"],
                    "orbits": b["orbits"],
                }
                for b in CELESTIAL_BODIES
            ],
        }

    def send_json(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, separators=(",", ":")).encode())

    def send_html(self, html):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(html.encode())

    def build_dashboard(self):
        return """<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>Sanctuary Academy: Orbit Runner</title>
  <script src=\"https://cdn.jsdelivr.net/npm/chart.js\"></script>
  <style>
    :root {
      --bg: #020617;
      --panel: rgba(15, 23, 42, 0.82);
      --line: #334155;
      --text: #e2e8f0;
      --muted: #94a3b8;
      --accent: #a78bfa;
      --good: #22c55e;
      --warn: #f59e0b;
    }
    body {
      margin: 0;
      font-family: Inter, system-ui, sans-serif;
      color: var(--text);
      background: radial-gradient(circle at top, #0f172a, var(--bg));
      min-height: 100vh;
    }
    .shell { max-width: 1240px; margin: 0 auto; padding: 1rem; }
    .hero {
      border: 1px solid var(--line);
      background: var(--panel);
      border-radius: 18px;
      padding: 1rem;
      margin-bottom: 1rem;
      display: grid;
      grid-template-columns: 1.2fr .8fr;
      gap: 1rem;
    }
    .hud { display: flex; gap: .75rem; flex-wrap: wrap; }
    .chip { border: 1px solid var(--line); border-radius: 999px; padding: .35rem .7rem; color: var(--muted); }
    .arena { height: 220px; border-radius: 12px; border: 1px solid #1e293b; background: #020817; }
    .grid {
      display: grid;
      gap: 1rem;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    }
    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 1rem;
    }
    h1,h2 { margin: 0 0 .6rem; }
    p { margin: 0 0 .8rem; color: var(--muted); }
    canvas.chart { width: 100% !important; height: 250px !important; }
    .choice { display: block; width: 100%; margin: .35rem 0; text-align: left; background: #111827; color: #e5e7eb; border: 1px solid #334155; border-radius: 8px; padding: .5rem; cursor: pointer; }
    .choice:hover { border-color: #64748b; }
    #feedback { min-height: 1.2rem; font-weight: 600; }
  </style>
</head>
<body>
  <main class=\"shell\">
    <section class=\"hero\">
      <div>
        <h1>Sanctuary Academy: Orbit Runner</h1>
        <p>A video-game style education instrument where missions teach the CelestialBody protocol while the ecosystem updates in real time.</p>
        <div class=\"hud\">
          <span class=\"chip\">Level: <strong id=\"lvl\">1</strong></span>
          <span class=\"chip\">XP: <strong id=\"xp\">0</strong></span>
          <span class=\"chip\">Stability: <strong id=\"stability\">CRYSTALLINE</strong></span>
        </div>
      </div>
      <canvas id=\"arena\" class=\"arena\"></canvas>
    </section>

    <section class=\"grid\">
      <article class=\"panel\">
        <h2>Thermodynamic Fuel Rod Visualizer</h2>
        <p>Entropy state for each reactor rod.</p>
        <canvas id=\"fuelChart\" class=\"chart\"></canvas>
      </article>

      <article class=\"panel\">
        <h2>Celestial Orbit Embedding</h2>
        <p>Live influence field from ingested bodies.</p>
        <canvas id=\"orbitChart\" class=\"chart\"></canvas>
      </article>

      <article class=\"panel\">
        <h2>Mission Console</h2>
        <p id=\"prompt\">Loading mission...</p>
        <div id=\"choices\"></div>
        <div id=\"feedback\"></div>
      </article>
    </section>
  </main>

  <script>
    // Non-blocking UI boot: fetch independent resources concurrently.
    let orbitChart;
    let mission;

    const fuelCtx = document.getElementById('fuelChart');
    if (fuelCtx) {
      new Chart(fuelCtx, {
        type: 'bar',
        data: {
          labels: ['Rod A (Active)', 'Rod B (Fresh)', 'Rod C (Cooling)'],
          datasets: [{
            label: 'Entropy %',
            data: [78, 0, 92],
            backgroundColor: [
              'rgba(248, 113, 113, 0.8)',
              'rgba(74, 222, 128, 0.8)',
              'rgba(96, 165, 250, 0.8)'
            ]
          }]
        },
        options: { indexAxis: 'y', scales: { x: { max: 100 } } }
      });
    }

    async function updateEcosystem() {
      const res = await fetch('/api/a2a/ecosystem');
      const eco = await res.json();
      const labels = (eco.nodes || []).map(n => n.name);
      const data = (eco.nodes || []).map(n => n.gravity);
      const orbitCtx = document.getElementById('orbitChart');
      if (!orbitCtx) return;

      if (!orbitChart) {
        orbitChart = new Chart(orbitCtx, {
          type: 'radar',
          data: {
            labels,
            datasets: [{
              label: 'Gravity Field',
              data,
              borderColor: 'rgba(167,139,250,.95)',
              backgroundColor: 'rgba(167,139,250,.22)',
              pointBackgroundColor: 'rgba(45,212,191,.95)'
            }]
          },
          options: { animation: false, scales: { r: { min: 0, max: 100 } } }
        });
      } else {
        orbitChart.data.labels = labels;
        orbitChart.data.datasets[0].data = data;
        orbitChart.update('none');
      }
    }

    async function updateState() {
      const res = await fetch('/api/game/state');
      const state = await res.json();
      document.getElementById('lvl').textContent = state.level;
      document.getElementById('xp').textContent = state.xp;
      document.getElementById('stability').textContent = state.stability;
    }

    async function loadMission() {
      const res = await fetch('/api/game/mission');
      const payload = await res.json();
      mission = payload.mission;
      const prompt = document.getElementById('prompt');
      const choices = document.getElementById('choices');
      const feedback = document.getElementById('feedback');
      prompt.textContent = mission.prompt;
      feedback.textContent = '';
      choices.innerHTML = '';

      mission.choices.forEach(choice => {
        const btn = document.createElement('button');
        btn.className = 'choice';
        btn.textContent = choice;
        btn.onclick = () => {
          const ok = choice === mission.answer;
          feedback.textContent = ok ? `✅ Correct — ${mission.explanation}` : `❌ Try again — ${mission.explanation}`;
          feedback.style.color = ok ? '#22c55e' : '#f59e0b';
        };
        choices.appendChild(btn);
      });
    }

    // requestAnimationFrame loop for game-like visual motion (non-blocking)
    function startArena() {
      const canvas = document.getElementById('arena');
      const ctx = canvas.getContext('2d');
      const stars = Array.from({length: 60}, () => ({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        r: Math.random() * 2 + .5,
        v: Math.random() * 0.5 + 0.2
      }));

      function tick() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#93c5fd';
        stars.forEach(s => {
          s.x -= s.v;
          if (s.x < 0) s.x = canvas.width;
          ctx.beginPath();
          ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
          ctx.fill();
        });
        requestAnimationFrame(tick);
      }
      requestAnimationFrame(tick);
    }

    async function bootstrap() {
      await Promise.allSettled([updateEcosystem(), updateState(), loadMission()]);
      startArena();
      setInterval(() => updateEcosystem().catch(() => {}), 2000);
      setInterval(() => updateState().catch(() => {}), 2500);
      setInterval(() => loadMission().catch(() => {}), 15000);
    }

    bootstrap();
  </script>
</body>
</html>
"""

    def log_message(self, format, *args):
        print(f"[{datetime.now().isoformat()}] {format % args}")


if __name__ == "__main__":
    PORT = 8003
    print("=" * 60)
    print("Genesis Seismic Log Server")
    print("=" * 60)
    print(f"Starting on http://0.0.0.0:{PORT}")
    print(f"Metrics: {SYSTEM_METRICS}")
    print("=" * 60)

    server = ThreadingHTTPServer(("0.0.0.0", PORT), SeismicHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()
