#!/bin/bash
TEXT="$1"
if command -v termux-tts-speak &> /dev/null; then
    termux-tts-speak "$TEXT"
elif command -v espeak &> /dev/null; then
    espeak "$TEXT"
else
    echo "[XARVIS]: $TEXT"
fi
