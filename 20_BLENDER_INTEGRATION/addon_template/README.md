# Addon template — Xarvis Blender Connector

This folder contains a minimal Blender addon template that starts a small **local HTTP JSON endpoint** when enabled.

Security and usage
- The server binds to 127.0.0.1 by default. **Do not** bind to public interfaces.
- The addon exposes basic commands: `ping` and `list_objects` (the latter requires Blender `bpy`).

Install
1. Copy the `addon_template` folder into Blender's addons directory or add it via Preferences > Add-ons > Install... (zip it first).
2. Enable the addon; it will start the small HTTP server bound to 127.0.0.1:47211 by default.
3. From your client (this repo) you can POST JSON to `http://127.0.0.1:47211/` like `{"action":"ping"}` or `{"action":"list_objects"}`.

Notes
- This is intentionally minimal: it's an integration starting point. For production you should add authentication (token file or binding checks) and whitelisting of commands.
- Use this only on trusted machines or in development environments.
