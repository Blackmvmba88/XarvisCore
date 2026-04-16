Automation README

This folder contains scripts to bootstrap the project, install Karabiner rules, add Spanish input source helper, and install/load LaunchAgents.

Scripts:
- `scripts/bootstrap.sh`: creates a virtualenv, installs Python dependencies, and runs `npm install` in `web/` if present.
- `scripts/start_services.sh`: starts backend (uvicorn) and frontend (vite) in background and writes logs to `logs/`.
- `scripts/install_karabiner.sh`: installs Karabiner-Elements via Homebrew and copies the rule JSON to Karabiner assets folder. You must enable the rule in Karabiner UI.
- `scripts/install_launchagents.sh`: copies plist files to `~/Library/LaunchAgents` and uses `launchctl` to load them. You will be prompted by macOS for permissions when necessary.
- `scripts/add_spanish_input_source.applescript`: opens System Settings to the keyboard section so you can add Spanish input source (requires UI interaction).

Notes & Safety:
- I will not execute these scripts automatically until you explicitly ask me to run them here.
- Some actions require user approval / accessibility permissions (Karabiner, AppleScript, LaunchAgents), and macOS will prompt you.
- LaunchAgents created assume the repo is located at: `~/untitled folder 2`. If your path differs, edit the plist files before installing.

How to run (manual):
1. Review scripts in the `scripts/` and `launchagents/` folders.
2. Make the scripts executable: `chmod +x scripts/*.sh`.
3. Run `scripts/bootstrap.sh` to set up the env and install deps.
4. Run `scripts/start_services.sh` to start services now, or `scripts/install_launchagents.sh` to install/start them as LaunchAgents.
5. To install Karabiner rule: `scripts/install_karabiner.sh` and then open Karabiner to enable the rule.
6. To add Spanish input source via UI helper: `osascript scripts/add_spanish_input_source.applescript`.
