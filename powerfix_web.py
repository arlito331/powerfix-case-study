#!/usr/bin/env python3
"""
PowerFix Case Study Generator — local web app.

Run:
    python3 powerfix_web.py

Then open http://localhost:5050 in your browser.
No extra dependencies — uses only the Python standard library.
"""

import os
import sys
import json
import threading
import subprocess
import webbrowser
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

HERE = os.path.dirname(os.path.abspath(__file__))
PORT = 5050

# ── In-memory job state (single-user local tool) ──────────────────────────
JOB = {
    "running": False,
    "log": [],
    "status": "idle",     # idle | running | done | error
    "pdf_path": None,
    "territory": None,
}
JOB_LOCK = threading.Lock()


def run_job(territory: str, case_number: str):
    with JOB_LOCK:
        JOB["running"] = True
        JOB["log"] = []
        JOB["status"] = "running"
        JOB["pdf_path"] = None
        JOB["territory"] = territory

    args = [sys.executable, os.path.join(HERE, "auto_case.py"), territory]
    if case_number:
        args += ["--case-number", case_number]

    pdf_path = None
    try:
        proc = subprocess.Popen(
            args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, cwd=HERE, env=os.environ.copy()
        )
        for line in proc.stdout:
            line = line.rstrip()
            with JOB_LOCK:
                JOB["log"].append(line)
            if "PDF saved" in line or "PDF written" in line:
                pdf_path = line.split(": ", 1)[-1].strip()
        proc.wait()

        if not pdf_path:
            out_dir = os.path.join(HERE, "output")
            safe = territory.replace(" ", "_")
            if os.path.isdir(out_dir):
                for f in sorted(os.listdir(out_dir), reverse=True):
                    if safe in f and f.endswith(".pdf"):
                        pdf_path = os.path.join(out_dir, f)
                        break

        with JOB_LOCK:
            JOB["status"] = "done" if proc.returncode == 0 else "error"
            JOB["pdf_path"] = pdf_path
            JOB["running"] = False
    except Exception as exc:
        with JOB_LOCK:
            JOB["log"].append(f"ERROR: {exc}")
            JOB["status"] = "error"
            JOB["running"] = False


PAGE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>PowerFix · Case Study Generator</title>
<style>
  :root { --amber: #E69500; --green: #2E7D32; --red: #C62828; }
  * { box-sizing: border-box; }
  body {
    font-family: -apple-system, "Helvetica Neue", Arial, sans-serif;
    max-width: 640px; margin: 40px auto; padding: 0 24px; color: #222;
  }
  h1 { color: var(--amber); margin-bottom: 0; font-size: 26px; }
  .subtitle { color: #666; margin-top: 4px; margin-bottom: 24px; }
  label { font-weight: 600; display: block; margin-bottom: 6px; }
  input[type=text] {
    font-size: 16px; padding: 10px 12px; width: 100%; max-width: 360px;
    border: 1px solid #ccc; border-radius: 6px;
  }
  .row { display: flex; gap: 16px; align-items: flex-end; margin-bottom: 18px; flex-wrap: wrap; }
  .case-num { width: 90px !important; }
  button {
    font-size: 15px; font-weight: 600; color: white; background: var(--amber);
    border: none; border-radius: 6px; padding: 12px 22px; cursor: pointer;
  }
  button:disabled { background: #aaa; cursor: not-allowed; }
  button.open { background: var(--green); margin-top: 10px; display: none; }
  #status { font-weight: 600; margin: 10px 0; color: #666; }
  #status.ok { color: var(--green); }
  #status.err { color: var(--red); }
  progress { width: 100%; height: 6px; display: none; }
  pre#log {
    background: #1e1e1e; color: #ccc; padding: 14px; border-radius: 8px;
    height: 280px; overflow-y: auto; font-size: 12px; line-height: 1.5;
    white-space: pre-wrap; word-break: break-word;
  }
  .footer { color: #bbb; font-size: 11px; margin-top: 16px; }
  hr { border: none; border-top: 1px solid #eee; margin: 20px 0; }
</style>
</head>
<body>
  <h1>PowerFix</h1>
  <div class="subtitle">Case Study Generator — type a territory, get a finished PDF.</div>
  <hr>

  <label for="territory">Territory</label>
  <div class="row">
    <input type="text" id="territory" placeholder="e.g. Peru" autofocus>
    <div>
      <label for="caseNum" style="font-size:12px;color:#888;">Case #</label>
      <input type="text" id="caseNum" class="case-num" placeholder="auto">
    </div>
    <button id="genBtn" onclick="generate()">Generate PDF →</button>
  </div>

  <div id="status">Ready. Enter a territory above and click Generate.</div>
  <progress id="bar"></progress>

  <hr>
  <div style="color:#888; font-size:12px; margin-bottom:6px;">Research log</div>
  <pre id="log"></pre>
  <button id="openBtn" class="open">Open PDF ↗</button>

  <div class="footer">Powered by Claude claude-opus-4-8 + web_search</div>

<script>
let polling = null;
let lastPdf = null;

document.getElementById('territory').addEventListener('keydown', e => {
  if (e.key === 'Enter') generate();
});

function generate() {
  const territory = document.getElementById('territory').value.trim();
  if (!territory) { alert('Please enter a territory name.'); return; }
  const caseNum = document.getElementById('caseNum').value.trim();

  document.getElementById('genBtn').disabled = true;
  document.getElementById('openBtn').style.display = 'none';
  document.getElementById('log').textContent = '';
  document.getElementById('bar').style.display = 'block';
  setStatus('⏳ Researching ' + territory + ' …', '');

  fetch('/generate', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({territory, caseNum})
  }).then(() => { poll(); });
}

function setStatus(text, cls) {
  const el = document.getElementById('status');
  el.textContent = text;
  el.className = cls;
}

function poll() {
  if (polling) clearInterval(polling);
  polling = setInterval(() => {
    fetch('/status').then(r => r.json()).then(data => {
      document.getElementById('log').textContent = data.log.join('\\n');
      document.getElementById('log').scrollTop = 1e9;

      if (data.status === 'running') {
        setStatus('⏳ Researching ' + data.territory + ' …', '');
      } else if (data.status === 'done') {
        clearInterval(polling);
        document.getElementById('genBtn').disabled = false;
        document.getElementById('bar').style.display = 'none';
        setStatus('✓ Case study ready!', 'ok');
        if (data.pdf_path) {
          lastPdf = data.pdf_path;
          const ob = document.getElementById('openBtn');
          ob.style.display = 'inline-block';
          ob.onclick = () => fetch('/open?path=' + encodeURIComponent(lastPdf));
        }
      } else if (data.status === 'error') {
        clearInterval(polling);
        document.getElementById('genBtn').disabled = false;
        document.getElementById('bar').style.display = 'none';
        setStatus('✗ Something went wrong — see log below', 'err');
      }
    });
  }, 800);
}
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # silence default request logging

    def _send_json(self, obj, code=200):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/":
            body = PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        elif parsed.path == "/status":
            with JOB_LOCK:
                self._send_json({
                    "status": JOB["status"],
                    "log": JOB["log"],
                    "pdf_path": JOB["pdf_path"],
                    "territory": JOB["territory"],
                })

        elif parsed.path == "/open":
            qs = parse_qs(parsed.query)
            path = qs.get("path", [None])[0]
            out_dir = os.path.realpath(os.path.join(HERE, "output"))
            if path and os.path.realpath(path).startswith(out_dir) and os.path.exists(path):
                subprocess.call(["open", path])
                self._send_json({"ok": True})
            else:
                self._send_json({"ok": False, "error": "invalid path"}, 400)

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if urlparse(self.path).path == "/generate":
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length) or b"{}")
            territory = (data.get("territory") or "").strip()
            case_num = (data.get("caseNum") or "").strip()

            if not territory:
                self._send_json({"ok": False, "error": "missing territory"}, 400)
                return
            if not re.match(r"^[A-Za-z0-9 ,.'\-]{1,80}$", territory):
                self._send_json({"ok": False, "error": "invalid territory"}, 400)
                return
            if case_num and not case_num.isdigit():
                self._send_json({"ok": False, "error": "invalid case number"}, 400)
                return

            with JOB_LOCK:
                if JOB["running"]:
                    self._send_json({"ok": False, "error": "a job is already running"}, 409)
                    return

            threading.Thread(target=run_job, args=(territory, case_num), daemon=True).start()
            self._send_json({"ok": True})
        else:
            self.send_response(404)
            self.end_headers()


def main():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("WARNING: ANTHROPIC_API_KEY is not set in this shell.")
        print("Run:  export ANTHROPIC_API_KEY='sk-ant-...'  before generating.\n")

    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    url = f"http://127.0.0.1:{PORT}"
    print(f"PowerFix web app running at {url}")
    print("Press Ctrl+C to stop.")
    threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
