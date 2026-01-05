#!/usr/bin/env python3
"""Connector minimal para ejecutar Blender headless desde este repo.

Ejecuta un script de ejemplo dentro de Blender y recoge la salida JSON.
"""
import argparse
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path


def find_blender(blender_bin: str | None) -> str:
    if blender_bin:
        return blender_bin
    # confiar en PATH
    from shutil import which

    b = which('blender')
    if b:
        return b
    raise FileNotFoundError('No se encontró Blender en PATH. Pasa --blender-bin /ruta/a/blender')


def _extract_json_from_text(text: str):
    # Busca el primer objeto JSON en el stdout
    m = re.search(r"(\{.*\})", text, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except Exception:
        return None


def run_blender_script(blender_bin: str, script_path: Path, extra_args: list[str] | None = None):
    cmd = [blender_bin, '--background', '--python', str(script_path)]
    if extra_args:
        cmd += extra_args
    print('Ejecutando:', ' '.join(shlex.quote(c) for c in cmd))
    proc = subprocess.run(cmd, capture_output=True, text=True)
    stdout = proc.stdout or ''
    stderr = proc.stderr or ''
    print('--- stdout ---')
    print(stdout)
    print('--- stderr ---')
    print(stderr, file=sys.stderr)
    parsed = _extract_json_from_text(stdout)
    return proc.returncode, stdout, stderr, parsed


def run_example(blender_bin: str):
    repo_root = Path(__file__).resolve().parents[1]
    example = repo_root / '20_BLENDER_INTEGRATION' / 'blender_example.py'
    if not example.exists():
        raise FileNotFoundError(f'No existe script de ejemplo: {example}')

    return run_blender_script(blender_bin, example)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--blender-bin', help='Ruta al ejecutable blender (opcional, si está en PATH no es necesario)')
    p.add_argument('--run-example', action='store_true', help='Ejecutar ejemplo dentro de Blender')
    p.add_argument('--script', help='Ejecutar script dentro de 20_BLENDER_INTEGRATION (nombre del archivo)')
    args = p.parse_args()

    try:
        blender = find_blender(args.blender_bin)
    except FileNotFoundError as e:
        print(e, file=sys.stderr)
        sys.exit(2)

    if args.run_example:
        rc, out, err, parsed = run_example(blender)
        if parsed is not None:
            print('\n--- PARSED JSON ---')
            print(json.dumps(parsed, indent=2, ensure_ascii=False))
        sys.exit(rc)

    if args.script:
        repo_root = Path(__file__).resolve().parents[1]
        script_path = repo_root / '20_BLENDER_INTEGRATION' / args.script
        if not script_path.exists():
            print(f'Script no encontrado: {script_path}', file=sys.stderr)
            sys.exit(3)
        rc, out, err, parsed = run_blender_script(blender, script_path)
        if parsed is not None:
            print('\n--- PARSED JSON ---')
            print(json.dumps(parsed, indent=2, ensure_ascii=False))
        sys.exit(rc)

    print('Conector listo. Pasa --run-example o --script <nombre>.')


if __name__ == '__main__':
    main()
