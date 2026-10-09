"""six-dialects · the page.

The engine already reads a project in six grammars. This is the part that lets
someone use it without opening a terminal: five fields, one button.

Standard library only. No framework, no build step, no bundle. The page is one
string in this file, served by http.server, and the review runs in-process
through the same review() the command line calls.
"""

from __future__ import annotations

import json
import threading
import time
import webbrowser
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .client import EndpointError
from .review import review as run_review
from .run import load_dialects

# A project description is a few sentences. Anything past this is either a
# mistake or someone trying to spend the operator's money in one request.
MAX_BODY = 24_000        # bytes of request body
MAX_FIELD = 6_000        # characters kept from any single field

# Every reading costs money at the far end. This is not security, it is a
# ceiling: it stops a loop from running all night before anyone notices.
RATE_LIMIT = 8           # readings
RATE_WINDOW = 3600       # per this many seconds, per address


class RateLimiter:
    """Fixed window per client address. Small, in memory, good enough."""

    def __init__(self, limit: int = RATE_LIMIT, window: int = RATE_WINDOW):
        self.limit = limit
        self.window = window
        self._seen: dict[str, deque] = {}
        self._lock = threading.Lock()

    def allow(self, who: str) -> bool:
        now = time.monotonic()
        with self._lock:
            hits = self._seen.setdefault(who, deque())
            while hits and now - hits[0] > self.window:
                hits.popleft()
            if len(hits) >= self.limit:
                return False
            hits.append(now)
            if len(self._seen) > 2048:  # do not grow without bound
                for key in [k for k, v in self._seen.items() if not v]:
                    del self._seen[key]
            return True

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Six Dialects</title>
<style>
  :root {
    --ink: #16150f;
    --muted: #6b6a60;
    --line: #dedbcf;
    --paper: #faf8f2;
    --card: #ffffff;
    --accent: #7a2718;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --ink: #ece9df; --muted: #97948a; --line: #33322c;
      --paper: #16150f; --card: #1d1c16; --accent: #d98b6a;
    }
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; background: var(--paper); color: var(--ink);
    font: 16px/1.6 Georgia, "Iowan Old Style", "Times New Roman", serif;
  }
  .wrap { max-width: 46rem; margin: 0 auto; padding: 3.5rem 1.5rem 6rem; }
  header { border-bottom: 1px solid var(--line); padding-bottom: 1.5rem; margin-bottom: 2.5rem; }
  h1 { font-size: 2rem; margin: 0 0 .4rem; letter-spacing: -0.01em; }
  .sub { color: var(--muted); margin: 0; font-size: .95rem; }
  .grammars { margin-top: 1rem; font-size: .85rem; color: var(--muted); }
  label { display: block; margin: 1.6rem 0 .4rem; font-size: .8rem;
          letter-spacing: .09em; text-transform: uppercase;
          font-family: ui-sans-serif, system-ui, sans-serif; }
  .hint { display: block; text-transform: none; letter-spacing: 0;
          font-size: .85rem; color: var(--muted); margin-top: .25rem;
          font-family: Georgia, serif; }
  textarea, input {
    width: 100%; padding: .7rem .8rem; font: inherit; font-size: .95rem;
    color: var(--ink); background: var(--card);
    border: 1px solid var(--line); border-radius: 3px;
  }
  textarea { min-height: 8rem; resize: vertical; }
  textarea:focus, input:focus { outline: 2px solid var(--accent); outline-offset: 1px; }
  button {
    margin-top: 2rem; padding: .75rem 1.9rem; font-size: 1rem;
    font-family: ui-sans-serif, system-ui, sans-serif;
    background: var(--ink); color: var(--paper);
    border: 0; border-radius: 3px; cursor: pointer;
  }
  button:disabled { opacity: .45; cursor: default; }
  .status { margin-top: 1.5rem; color: var(--muted); font-size: .95rem; min-height: 1.6rem; }
  .err { color: var(--accent); }
  section.result { margin-top: 3.5rem; }
  .reading { border-top: 1px solid var(--line); padding: 1.6rem 0; }
  .reading h3 { margin: 0 0 .2rem; font-size: 1.15rem; }
  .speaks { color: var(--muted); font-size: .85rem;
            font-family: ui-sans-serif, system-ui, sans-serif; }
  .field { margin-top: .9rem; }
  .field .k { font-size: .72rem; letter-spacing: .09em; text-transform: uppercase;
              color: var(--muted); font-family: ui-sans-serif, system-ui, sans-serif; }
  .field p { margin: .2rem 0 0; }
  .block { margin-top: 3rem; padding-top: 1.6rem; border-top: 2px solid var(--ink); }
  .block h2 { font-size: .8rem; letter-spacing: .14em; text-transform: uppercase;
              margin: 0 0 1rem; font-family: ui-sans-serif, system-ui, sans-serif; }
  .fork { margin-bottom: 1.2rem; }
  .fork .pair { font-weight: bold; }
  .moment { font-size: 1.15rem; line-height: 1.65; }
  .carry { font-style: italic; font-size: 1.1rem; }
  footer { margin-top: 4rem; padding-top: 1.5rem; border-top: 1px solid var(--line);
           color: var(--muted); font-size: .82rem; }
  footer a { color: inherit; }
</style>
</head>
<body>
<div class="wrap">

<header>
  <h1>Six Dialects</h1>
  <p class="sub">Describe what you are building. It reads your project in six moral grammars,
     shows you where two of them contradict each other, and names the point where a person
     stops deciding.</p>
  <p class="grammars">Brussels starts from rights · Washington from liberty ·
     Beijing from the stability of the group · London from catastrophic risk ·
     Singapore from compliance · Rome from dignity</p>
</header>

<form id="f">
  <label for="project">What you are building
    <span class="hint">In your own words. A few sentences is enough.</span></label>
  <textarea id="project" required
    placeholder="A tool that reads CVs and ranks candidates for a shortlist."></textarea>

  <label for="used_by">Who operates it
    <span class="hint">The person with their hands on it.</span></label>
  <input id="used_by" placeholder="A recruiter at a mid-size company">

  <label for="affects">Who it affects
    <span class="hint">Often not the same person.</span></label>
  <input id="affects" placeholder="Applicants, who never see it">

  <label for="decides">What it decides or recommends
    <span class="hint">The output a human then acts on.</span></label>
  <input id="decides" placeholder="Which twelve of two hundred applications get read">

  <label for="region">Where it is used, and in which language</label>
  <input id="region" placeholder="Germany and Poland, in English">

  <button id="go" type="submit">Read it in six grammars</button>
  <div class="status" id="status"></div>
</form>

<section class="result" id="out" hidden></section>

<footer>
  Six Dialects reads your project. It does not tell you whether you comply, and it does not
  pick a grammar for you. Nothing you type is stored.<br>
  Created by Nicoletta Iacobacci · Apache 2.0 ·
  <a href="https://github.com/NicIaco/six-dialects">github.com/NicIaco/six-dialects</a> ·
  <a href="https://doi.org/10.5281/zenodo.22145171">10.5281/zenodo.22145171</a>
</footer>

</div>

<script>
const DIALECTS = __DIALECTS__;
const form = document.getElementById('f');
const btn = document.getElementById('go');
const status = document.getElementById('status');
const out = document.getElementById('out');

const WAIT = [
  'Reading it in six grammars.',
  'Brussels, Washington, Beijing, London, Singapore, Rome.',
  'Looking for where two of them contradict each other.',
  'Looking for the moment a person stops deciding.',
  'Still working. A careful reading takes about a minute.'
];

function el(tag, cls, text) {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text !== undefined) n.textContent = text;
  return n;
}

function field(k, v) {
  const d = el('div', 'field');
  d.append(el('div', 'k', k), el('p', null, v || ''));
  return d;
}

function render(data) {
  out.replaceChildren();
  const order = Object.keys(DIALECTS);
  const readings = (data.readings || []).slice().sort(
    (a, b) => order.indexOf(a.dialect) - order.indexOf(b.dialect));

  for (const r of readings) {
    const spec = DIALECTS[r.dialect] || {};
    const box = el('div', 'reading');
    box.append(el('h3', null, spec.name || r.dialect));
    box.append(el('div', 'speaks', 'speaks ' + (spec.speaks || '')));
    box.append(field('assumes', r.assumes));
    box.append(field('reads as wrong', r.misreads));
    box.append(field('design decision', r.decision));
    out.append(box);
  }

  if ((data.tensions || []).length) {
    const b = el('div', 'block');
    b.append(el('h2', null, 'Forks · where two grammars contradict each other here'));
    for (const t of data.tensions) {
      const f = el('div', 'fork');
      const names = (t.between || []).map(p => (DIALECTS[p] || {}).name || p).join(' vs ');
      f.append(el('div', 'pair', names), el('div', null, t.about || ''));
      b.append(f);
    }
    out.append(b);
  }

  if (data.delegation_moment) {
    const b = el('div', 'block');
    b.append(el('h2', null, 'The moment'));
    b.append(el('p', 'moment', data.delegation_moment));
    out.append(b);
  }

  if (data.question) {
    const b = el('div', 'block');
    b.append(el('h2', null, 'Carry this'));
    b.append(el('p', 'carry', data.question));
    out.append(b);
  }

  out.hidden = false;
  out.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const body = {};
  for (const id of ['project', 'used_by', 'affects', 'decides', 'region']) {
    body[id] = document.getElementById(id).value.trim();
  }
  if (!body.project) return;

  btn.disabled = true;
  out.hidden = true;
  status.className = 'status';

  let i = 0;
  status.textContent = WAIT[0];
  const tick = setInterval(() => {
    i = Math.min(i + 1, WAIT.length - 1);
    status.textContent = WAIT[i];
  }, 12000);

  try {
    const res = await fetch('/api/review', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'the reading failed');
    status.textContent = '';
    render(data);
  } catch (err) {
    status.className = 'status err';
    status.textContent = String(err.message || err);
  } finally {
    clearInterval(tick);
    btn.disabled = false;
  }
});
</script>
</body>
</html>
"""


def _page(dialects: dict) -> bytes:
    slim = {
        did: {"name": spec.get("name", did), "speaks": spec.get("speaks", "")}
        for did, spec in dialects.items()
    }
    return PAGE.replace("__DIALECTS__", json.dumps(slim)).encode("utf-8")


def make_handler(endpoint, dialects: dict, behind_proxy: bool = False):
    page = _page(dialects)
    lock = threading.Lock()
    limiter = RateLimiter()

    class Handler(BaseHTTPRequestHandler):
        server_version = "six-dialects"
        protocol_version = "HTTP/1.1"

        def log_message(self, fmt, *args):  # quiet by default
            pass

        def _who(self) -> str:
            if behind_proxy:
                fwd = self.headers.get("X-Forwarded-For")
                if fwd:
                    return fwd.split(",")[0].strip()
            return self.client_address[0]

        def _send(self, code: int, body: bytes, ctype: str) -> None:
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _json(self, code: int, payload: dict) -> None:
            self._send(code, json.dumps(payload).encode("utf-8"),
                       "application/json; charset=utf-8")

        def do_GET(self) -> None:
            if self.path.split("?")[0] in ("/", "/index.html"):
                self._send(200, page, "text/html; charset=utf-8")
            else:
                self._json(404, {"error": "not found"})

        def do_HEAD(self) -> None:
            # uptime checkers ask with HEAD; answer instead of saying 501
            if self.path.split("?")[0] in ("/", "/index.html"):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(page)))
                self.end_headers()
            else:
                self.send_response(404)
                self.send_header("Content-Length", "0")
                self.end_headers()

        def _field(self, body: dict, name: str) -> str:
            return (body.get(name) or "")[:MAX_FIELD].strip()

        def do_POST(self) -> None:
            if self.path != "/api/review":
                self._json(404, {"error": "not found"})
                return

            try:
                length = int(self.headers.get("Content-Length") or 0)
            except ValueError:
                self._json(400, {"error": "could not read the form"})
                return

            if length > MAX_BODY:
                # drain nothing: answer and let the connection close
                self.close_connection = True
                self._json(413, {"error": "that description is too long. "
                                          "A few sentences is what this reads best."})
                return

            try:
                body = json.loads(self.rfile.read(length) or b"{}")
                if not isinstance(body, dict):
                    raise ValueError("not an object")
            except (ValueError, json.JSONDecodeError):
                self._json(400, {"error": "could not read the form"})
                return

            project = self._field(body, "project")
            if not project:
                self._json(400, {"error": "describe what you are building"})
                return

            if not limiter.allow(self._who()):
                self._json(429, {"error": "that is a lot of readings from one place. "
                                          "Try again in an hour, or run it on your own "
                                          "machine: github.com/NicIaco/six-dialects"})
                return

            # One reading at a time: the endpoint is shared and the page is
            # meant for one person thinking, not for traffic.
            try:
                with lock:
                    result = run_review(
                        endpoint, project, dialects,
                        used_by=self._field(body, "used_by"),
                        affects=self._field(body, "affects"),
                        region=self._field(body, "region"),
                        decides=self._field(body, "decides"),
                        context="",
                    )
            except EndpointError as exc:
                self._json(502, {"error": f"the model endpoint did not answer: {exc}"})
                return
            except ValueError as exc:
                self._json(502, {"error": f"the model did not answer in the expected shape: {exc}"})
                return

            self._json(200, result)

    return Handler


def serve(endpoint, host: str = "127.0.0.1", port: int = 8017,
          open_browser: bool = True, behind_proxy: bool = False) -> None:
    dialects = load_dialects()
    httpd = ThreadingHTTPServer(
        (host, port), make_handler(endpoint, dialects, behind_proxy=behind_proxy))
    url = f"http://{host}:{port}/"

    print(f"Six Dialects is at {url}")
    print("Stop it with Ctrl-C.")

    if open_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        httpd.server_close()
