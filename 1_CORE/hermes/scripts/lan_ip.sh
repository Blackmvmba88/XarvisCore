#!/usr/bin/env bash
# Helper to print LAN IP for telemetry usage.
(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo localhost)
