#!/usr/bin/env python3
"""WebUI mínimo para disparar comandos headless en Blender desde este repo.

Rutas:
- GET /        -> página con botones
- POST /run   -> ejecuta un comando (mapea a un script en 20_BLENDER_INTEGRATION) y muestra resultado JSON
"""
from flask import Flask, render_template, request, redirect, url_for, flash
import os
import json
from pathlib import Path
import subprocess
import sys
from typing import Optional

app = Flask(__name__)
app.secret_key = 'replace-me-in-prod'

REPO_ROOT = Path(__file__).resolve().parents[1]
BLENDER_INTEGRATION_DIR = REPO_ROOT / '20_BLENDER_INTEGRATION'

# Mapear comandos a scripts existentes
COMMANDS = {
    'list_objects': 'blender_example.py',
    # Puedes añadir más mapeos aquí: 'render': 'blender_render.py'
}

def run_script(script_name: str, blender_bin: Optional[str] = None):
    script_path = BLENDER_INTEGRATION_DIR / script_name
    if not script_path.exists():
        return {'error': f'script not found: {script_name}'}

    # Ejecutar connector como subprocess para aislar el entorno web
    connector = REPO_ROOT / '20_BLENDER_INTEGRATION' / 'connector.py'
    cmd = [sys.executable, str(connector), '--script', script_name]
    if blender_bin:
        cmd += ['--blender-bin', blender_bin]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    stdout = proc.stdout
    stderr = proc.stderr

    # Buscar JSON en stdout
    # El conector ya imprime PARSED JSON si lo encuentra; intentar parsear última línea JSON
    parsed = None
    try:
        # Buscar la última línea que empiece con '{'
        for line in reversed(stdout.splitlines()):
            line = line.strip()
            if line.startswith('{'):
                parsed = json.loads(line)
                break
    except Exception:
        parsed = None

    return {
        'returncode': proc.returncode,
        'stdout': stdout,
        'stderr': stderr,
        'json': parsed,
    }

@app.route('/')
def index():
    return render_template('index.html', commands=COMMANDS)

@app.route('/run', methods=['POST'])
def run():
    cmd_key = request.form.get('cmd')
    blender_bin = request.form.get('blender_bin') or None
    if cmd_key not in COMMANDS:
        flash('Comando desconocido', 'error')
        return redirect(url_for('index'))

    result = run_script(COMMANDS[cmd_key], blender_bin)
    return render_template('result.html', cmd=cmd_key, result=result)

if __name__ == '__main__':
    app.run(debug=True, port=7777)
