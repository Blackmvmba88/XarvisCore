# Mamba Guardian - System Monitor

This tool watches processes and automatically kills those exceeding configured CPU/RAM thresholds.

Paths:
- `mamba_guardian.py` - main script
- `guardian.sh` - launcher script (start/stop/status/logs)
- `guardian.log` - activity log
- `kills.json` - kill history

Web UI integration (HYDRA Organizer)
- Added endpoints in `00_ORGANIZED_MASTER/webui_app.py` under `/api/guardian/*`:
  - `GET /api/guardian/status` -> status output & last log tail
  - `POST /api/guardian/start` -> start the guardian (background)
  - `POST /api/guardian/stop` -> stop the guardian
  - `GET /api/guardian/logs?n=200` -> get last `n` lines

Usage examples (from web UI):
- Open the Organizer UI (`00_ORGANIZED_MASTER`), click the `GUARDIAN` tab and use Start/Stop/Refresh log buttons.

Security:
- Local tool intended for single-user usage on the USB; no authentication is implemented. Do not expose to untrusted networks.

Tuning:
- Adjust thresholds in `mamba_guardian.py` CONFIG to strike balance between being reactive and safe.

