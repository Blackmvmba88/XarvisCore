# Copilot Instructions — Xarvis Core (concise)

Purpose: quick, actionable guidance so an AI coding agent can be productive immediately in this repo.

## Quick setup ✅
- Create a venv at the repo root and activate it:
  ```bash
  python3 -m venv venv && source venv/bin/activate
  pip install -r requirements.txt && pip install -r dev-requirements.txt
  ```
- Target Python version: **3.11** (CI/dev target).

## Run & debug 🔧
- Run the whole stack (orchestrator uses `venv/bin/python3`):
  ```bash
  python3 xarvis_supervisor.py
  ```
- Run a single service (preferred from the service directory):
  ```bash
  cd <domain_dir>
  venv/bin/python3 <service>.py
  ```
- Logs are under `5_INFRA/logs/` (e.g., `master.log`, `core.log`, `full_power.log`). Supervisor restarts domains every ~15s when they exit.

## High-level architecture & patterns 🧭
- Domains: the repo is organized into domain folders (0..19); `xarvis_supervisor.py` orchestrates a subset via `PROCESSES` / `EXTENDED_PROCESSES`.
- Process pattern: each entry is {"path": <abs>, "log": <abs>, "proc": None, "priority": N, "enabled": Bool}. See `xarvis_supervisor.py` for exact usage (preexec, cwd, VENV_PYTHON).
- Long-running services:
  - `*_engine.py` — compute/worker engines.
  - `*_detector.py` — detectors with native deps and `start_*.sh` scripts to install/check native deps.
  - `*_protocol.py` — protocol modules typically expose a singleton (e.g., `gaia = GaiaProtocol()`, import `from gaia_protocol import gaia`).
- Optional local integrations often use `sys.path.insert` to import sibling domains (see `1_CORE/xarvis_core.py` for the quantum core guard).

## Domain-specific quickstarts & docs 📚
- Many domains include their own docs and GitHub instructions (e.g., `14_CREATIVE_TOOLS/ytdlp-web/.github/copilot-instructions.md`). Look for `.github/copilot-instructions.md` inside the domain before making changes.
- If a domain needs native packages, update `5_INFRA/setup_xarvis.sh` and add `start_*.sh` scripts that verify/install dependencies.

## Tests & running them 🧪
- Tests live under `tests/` and per-domain `*/tests/`.
- Quick run (skip slow): `pytest -q -m "not slow"`.
- To run a specific domain's tests: `pytest path/to/domain/tests -q` or use domain helper scripts (e.g., `10_CULTURAL_RENAISSANCE/run_all_tests.sh`).

## Platform & native deps 🖥️
- Primary dev target: **macOS**. Use Homebrew for native packages.
- Example native deps: `brew install chromaprint sox ffmpeg` (used by audio domains).
- Many services expect `venv/bin/python3` and relative `BASE_DIR` values—run code from the service folder for correct CWD behavior.

## Security & repo conventions 🔒
- Many files use a **hardcoded `BASE_DIR`** for local dev; prefer `.env` overrides or update `BASE_DIR` when testing in new environments (`xarvis_supervisor.py`, `xarvis_core.py`).
- Placeholder credentials appear in the code (e.g., `BlackSekhmet`/`Admin123`) — **never commit real secrets**. Use `.env` and `dotenv` in code.

## PR checklist (actionable) ✅
- Provide exact reproduction steps and commands (how to run the failing domain).
- Add or update tests (mark slow tests with `@pytest.mark.slow`).
- Update `5_INFRA/setup_xarvis.sh` if new native deps are required.
- Update `xarvis_supervisor.py` `PROCESSES` and create log files for new services.
- Document new environment variables, ports, and any special runtime steps in the domain README.

## Where to look (key files) 📂
- `xarvis_supervisor.py` — orchestration & process map
- `ARCHITECTURE.md` — high-level design
- `5_INFRA/setup_xarvis.sh` — native packages and install guidance
- `1_CORE/*` — core server, protocol singletons
- `10_CULTURAL_RENAISSANCE/*` — representative domain with detectors, audio tooling, test helpers

---

## 60s domain quickstarts (copy-pasteable) ⚡

### Hermes — the message/event gateway (60s)
- Purpose: single throat for messages, events, commands, telemetry.
- Run (full): cd 1_CORE/hermes && bash scripts/bootstrap_macos.sh && bash scripts/run_local.sh
- Run (api only): python services/api/app.py --host 0.0.0.0 --port 8788
- WebUI / API: WebUI -> http://localhost:8787, API -> http://localhost:8788
- Send a chat: curl -s -X POST http://localhost:8788/chat -H 'Content-Type: application/json' -d '{"message":"ping"}'
- Stream SSE: curl -N 'http://localhost:8788/chat/stream?q=hello'
- Telemetry: curl -s -X POST http://localhost:8788/telemetry -H 'Content-Type: application/json' -d '{"event":"ping","source":"test"}'
- Config: edit `configs/hermes.yaml` and `.env.example` (runtime.llm, rag.qdrant_url, QDRANT_URL)
- Notes: `/chat` returns a fallback string when LLMs are not installed; ingest with `python services/rag/ingest.py` to build `data/vectors/`.

### VPA — performance & actions (60s)
- Purpose: analyze vocal performances and persist actions (safe by design).
- Run: cd 10_CULTURAL_RENAISSANCE && python3 vocal_performance_analyzer.py (server port 9000)
- Dashboard/API: open `vpa_dashboard.html` or check `http://localhost:9000/status`
- Quick checks: curl -X POST http://localhost:9000/detect ; curl http://localhost:9000/performance
- Register/commit action: from REPL `from vocal_performance_analyzer import vpa; vpa.save_performance('test.json')`
- Dry-run: set `vpa.current_song = {...}` and call GET `/performance` without calling `save_performance()` to avoid persisting
- Permissions/limits: needs Shazam Desktop (or ShazamKit) + microphone permissions; install `afinador_suno` for pitch analysis
- Tests: see `10_CULTURAL_RENAISSANCE/test_audio_detector.py` and `start_vpa_detector.sh` for integration patterns.

### Suno Suite — music generation & pipeline (60s)
- Purpose: generate, manage, and serve Suno-produced music; data anchor = `~/Music/Suno` (do not move)
- Setup: export `SUNO_HOME=~/Music/Suno`; cd `10_CULTURAL_RENAISSANCE/suno-suite` and install relevant reqs (e.g. `apps/suno-headless/requirements.txt`)
- Headless test: `python3 apps/suno-headless/main.py` → connectivity & Chrome driver checks; add SUNO credentials per prompts
- Generate example: run `python3 apps/suno-headless/main.py` -> `generate_alejandro_song()` (or use `generate_song_headless(email,password,data)` programmatically)
- Web app: `make app-run` (see `apps/suno-suite-app/README.md`) — configure `.env.example` (SUNO_APP_PORT/SUNO_WS_TOKEN)
- Common failures: missing Chrome/driver, missing credentials, not logged-in session, missing `SUNO_HOME`, or rate-limits from Suno (respect delays)
- Tests: use `apps/suno-headless/test_connection.py` and `apps/suno-headless` pytest tests to validate environment.

## Quick tips for AI coding agents 🤖
- Check for per-domain `.github/copilot-instructions.md` before changing a domain — many have domain-specific commands and native-dep steps (example: `14_CREATIVE_TOOLS/ytdlp-web`).
- When adding new domains, follow the numeric folder pattern, add the process to `xarvis_supervisor.py` `PROCESSES`, and create a `5_INFRA/logs/<domain>.log` entry.
- Prefer small, well-scoped PRs: include reproduction steps, commands used, and focused tests. Mark long tests with `@pytest.mark.slow`.
- Look for protocol singletons (e.g., `gaia` in `gaia_protocol.py`) and reuse them where appropriate rather than creating new global state.

If any part of this is unclear or you'd like a per-domain quickstart added (Hermes, VPA, Suno, ytdlp_web, etc.), tell me which domain and I will add a short, copy-pasteable section that includes setup, native deps, run commands, and tests. 🎯

## Preview renders & CI (cybercam-blender) ⚡
- There is a manual workflow: **Actions → Preview Render (manual dispatch)** that runs quick tests and creates a preview artifact (`cybercam-preview-render`). It does not require Blender or GPU.
- The workflow is fail-fast: tests run first; if they fail the preview step is skipped. The preview job performs a **dry-run** of `scripts/dev/render_headless.sh` using `BLENDER_BIN=echo` to validate the shell glue, then creates a small PNG placeholder and uploads it as an artifact.
- To trigger it: go to the GitHub Actions UI, select “Preview Render (manual)”, click **Run workflow**. The artifact can be downloaded from the workflow run page (Artifacts section).
- Purpose: allow collaborators to preview pipeline outputs without Blender/GPU and ensure the rendering glue (flags, paths, env) is validated before adding any heavy GPU-based “Hero” workflows.

If you want, I can add a short README entry in `cybercam-blender/README.md` that references the workflow and the `render_headless.sh` dry-run. Let me know which you'd prefer.
