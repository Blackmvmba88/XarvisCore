# Addon template — Xarvis Blender Connector

This folder contains a minimal Blender addon template that starts a small **local HTTP JSON endpoint** when enabled.

Security and usage
- The server binds to 127.0.0.1 by default. **Do not** bind to public interfaces.
- The addon exposes basic commands: `ping` and `list_objects` (the latter requires Blender `bpy`).

Install
1. Copy the `addon_template` folder into Blender's addons directory or add it via Preferences > Add-ons > Install... (zip it first), or run the installer script `20_BLENDER_INTEGRATION/addon_template/install_blender_addon.sh`.
2. Enable the addon; it will start the small HTTP server bound to 127.0.0.1:47211 by default.
3. From your client (this repo) you can POST JSON to `http://127.0.0.1:47211/` like `{"action":"ping"}` or `{"action":"list_objects"}`.

Token-based authentication
- The addon supports a lightweight token file located at `~/.config/xarvis/blender.token`.
- You can create it with the installer script; the file must contain a single token string and be readable only by the user (chmod 600).
- When the addon preference **Require Token** is enabled (Preferences → Add-ons → Xarvis Connector Addon → Require Token), the server will require the HTTP header `Authorization: Bearer <token>` for privileged commands (render, export, run_operator, eval_safe).
- To rotate a token: overwrite `~/.config/xarvis/blender.token` with a new random token and restart the addon (or restart Blender). To invalidate: remove the token file or disable the require-token preference.

Notes
- This is intentionally minimal: it's an integration starting point. For production you should add authentication (token file or binding checks) and whitelisting of commands.
- Use this only on trusted machines or in development environments.

Progress semantics
- Long-running jobs (e.g., `render_animation`) will report a `progress` value in the job status response. The value is a float in the range 0.0..100.0 and represents the fraction of work completed (clamped).
- Progress is updated monotonically during the job and will reach `100.0` when the job completes successfully.
- If a cancel is requested, the job attempts a clean abort and will report status `cancelled` and a progress value less than `100.0`.
- Short or instantaneous jobs may return `progress: null` or omit it entirely.
- Clients should poll `get_job_status` to observe progress and detect completion/cancellation.

Frame hooks (optional, experimental)
- For more accurate progress, the addon can optionally use Blender's `frame_change_post` handler to update job progress based on the scene's `frame_current`.
- This feature is opt-in via the addon preference **Use Blender Frame Hooks (experimental)** or via the environment variable `XARVIS_BLENDER_FRAME_HOOKS=1` (tests/deploy convenience).
- The hook is best-effort and will register only when there are active jobs that requested frame hooks (e.g., `render_animation`) and will deregister automatically when no longer needed.
- The hook acts as a sensor: it reads `frame_current` and updates job `progress` but does not perform control actions, cancellation, or side effects.
- If Blender is not available, the system will still operate using per-frame updates from `render_animation` itself.
