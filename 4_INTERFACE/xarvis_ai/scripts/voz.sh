#!/data/data/com.termux/files/usr/bin/bash
text=$(cat response.txt)
termux-tts-speak "$text"