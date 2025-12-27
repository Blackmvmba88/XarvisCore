from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from typing import Optional

import tkinter as tk
from tkinter import ttk, messagebox
import random
import math
import numpy as np

from ..core.catalog import build_catalog, CatalogItem
from ..io.decode import ensure_analysis_mono16k
from ..core.player import Player
from ..core.f0 import extract_f0_offline, save_analysis_json
from ..core.ondemand import OnDemandF0
from ..core.mic import MicPitchDetector, PitchFrame
from ..core.sync import delta_cents
from ..util.music import hz_to_name_and_cents, hz_to_midi, midi_to_hz
from ..util import theme
import os

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ANALYSES_DIR = PROJECT_ROOT / "analyses"
SETTINGS_YML = PROJECT_ROOT / "settings.yml"


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Afinador Suno")
        self.geometry("900x600")

        self.catalog: list[CatalogItem] = []
        self.player = Player()
        self.mic = MicPitchDetector(sr=16000, hop_ms=10)
        self.analysis_cache: dict[str, Path] = {}

        self.offset_ms = tk.IntVar(value=0)
        self.a4_hz = tk.IntVar(value=440)
        self.threshold = tk.IntVar(value=25)

        # estado de objetivo actual
        self._last_target_hz: float = 0.0
        # animación y partículas
        self._needle_anim: float = 0.0
        self._particles: list[dict] = []
        # umbral adaptativo
        self._delta_hist: list[float] = []
        self._lock_counter: int = 0

        self._build_ui()
        # Estado para refresco de UI desde hilo principal
        self._last_ui = {
            "target_text": "Objetivo: -",
            "me_text": "Tu nota: -",
            "delta_text": "Δ cents: -",
            "needle": 0.0,
            "led": False,
        }
        self._ui_timer_ms = 67  # ~15 fps
        self.after(self._ui_timer_ms, self._ui_tick)

        self._refresh_catalog()
        # Pre-analizar en background si está habilitado (por defecto sí). Deshabilitar con AFINADOR_PREANALYZE=0
        if os.environ.get("AFINADOR_PREANALYZE", "1") != "0":
            self._start_preanalysis_background()

    def _build_ui(self) -> None:
        self.left = ttk.Frame(self)
        left = self.left
        left.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=8)

        self.right = ttk.Frame(self)
        right = self.right
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=8, pady=8)

        ttk.Label(left, text="Canciones (Suno / Descargas)").pack(anchor=tk.W)
        self.listbox = tk.Listbox(left, width=45, height=28)
        self.listbox.pack(fill=tk.Y)

        btns = ttk.Frame(left)
        btns.pack(fill=tk.X, pady=6)
        ttk.Button(btns, text="Analizar", command=self.on_analyze).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="Analizar todo (rápido)", command=self.on_analyze_all_fast).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="Play + Tuner", command=self.on_play).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="Tuner clásico", command=self.on_tuner_classic).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="Stop", command=self.on_stop).pack(side=tk.LEFT, padx=4)

        # Settings
        settings = ttk.Labelframe(left, text="Ajustes")
        settings.pack(fill=tk.X, pady=6)
        ttk.Label(settings, text="Offset (ms)").grid(row=0, column=0, sticky=tk.W)
        tk.Scale(settings, from_=-1000, to=1000, orient=tk.HORIZONTAL, variable=self.offset_ms).grid(row=0, column=1, sticky=tk.EW)
        ttk.Label(settings, text="A4 (Hz)").grid(row=1, column=0, sticky=tk.W)
        tk.Scale(settings, from_=430, to=450, orient=tk.HORIZONTAL, variable=self.a4_hz).grid(row=1, column=1, sticky=tk.EW)
        ttk.Label(settings, text="Umbral (cents)").grid(row=2, column=0, sticky=tk.W)
        tk.Scale(settings, from_=5, to=50, orient=tk.HORIZONTAL, variable=self.threshold).grid(row=2, column=1, sticky=tk.EW)
        # Umbral adaptativo
        self.auto_threshold = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings, text="Umbral adaptativo", variable=self.auto_threshold).grid(row=3, column=0, sticky=tk.W)
        # Auto-octava y Modo simple
        self.auto_octave = tk.BooleanVar(value=False)
        ttk.Checkbutton(settings, text="Auto-octava", variable=self.auto_octave).grid(row=3, column=1, sticky=tk.W)
        self.simple_mode = tk.BooleanVar(value=False)
        ttk.Checkbutton(settings, text="Modo simple", variable=self.simple_mode, command=self._apply_simple_mode).grid(row=3, column=2, sticky=tk.W)
        # Analizar antes de reproducir
        self.play_analyze_first = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings, text="Analizar antes de reproducir", variable=self.play_analyze_first).grid(row=3, column=3, sticky=tk.W)
        # Calibración y sensibilidad de voz
        self.sensitivity = tk.IntVar(value=50)
        ttk.Button(settings, text="Calibrar silencio", command=self._calibrate_noise).grid(row=4, column=0, sticky=tk.W)
        tk.Scale(settings, from_=0, to=100, orient=tk.HORIZONTAL, variable=self.sensitivity).grid(row=4, column=1, sticky=tk.EW)
        # Transposición para adaptar registro (mujer->hombre: -12 semitonos recomendado)
        self.transpose = tk.IntVar(value=0)
        ttk.Label(settings, text="Transposición (semitonos)").grid(row=3, column=0, sticky=tk.W)
        tk.Scale(settings, from_=-12, to=12, orient=tk.HORIZONTAL, variable=self.transpose).grid(row=5, column=1, sticky=tk.EW)
        settings.columnconfigure(1, weight=1)

        # Right: needle
        self.canvas = tk.Canvas(right, bg=theme.BG, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self._draw_needle(0.0)

        # Info labels
        info = ttk.Frame(right)
        info.pack(fill=tk.X)
        self.lbl_target = ttk.Label(info, text="Objetivo: -")
        self.lbl_me = ttk.Label(info, text="Tu nota: -")
        self.lbl_delta = ttk.Label(info, text="Δ cents: -")
        for w in (self.lbl_target, self.lbl_me, self.lbl_delta):
            w.pack(side=tk.LEFT, padx=12)
        # LED de afinación
        self.led = tk.Canvas(info, width=18, height=18, bg=theme.PANEL_BG, highlightthickness=0)
        self.led.pack(side=tk.RIGHT, padx=8)
        self._draw_led(False)

        # Estado grande (Modo simple)
        self.lbl_state_big = tk.Label(right, text="", font=("Helvetica", 28, "bold"), fg=theme.TEXT, bg=theme.BG)
        # Se mostrará/ocultará según el modo simple

        # Barra de estado
        self.status = ttk.Label(self, text="Listo", anchor=tk.W)
        self.status.pack(fill=tk.X, side=tk.BOTTOM)

    def _draw_needle(self, cents: float, led_on: bool = False, rms: float = 0.0) -> None:
        self.canvas.delete("all")
        w = self.canvas.winfo_width() or 800
        h = self.canvas.winfo_height() or 400
        cx, cy = w // 2, h // 2
        max_cents = 50
        # zonas de color (rojo, amarillo, verde)
        def X(c):
            return cx + int((c / max_cents) * (w//2 - 60))
        y1, y2 = cy - 24, cy + 24
        # rojo
        self.canvas.create_rectangle(X(-50), y1, X(-20), y2, fill=theme.DANGER, width=0)
        self.canvas.create_rectangle(X(20), y1, X(50), y2, fill=theme.DANGER, width=0)
        # amarillo
        self.canvas.create_rectangle(X(-20), y1, X(-10), y2, fill=theme.WARNING, width=0)
        self.canvas.create_rectangle(X(10), y1, X(20), y2, fill=theme.WARNING, width=0)
        # verde centro
        self.canvas.create_rectangle(X(-10), y1, X(10), y2, fill=theme.SUCCESS, width=0)
        # línea y marcas sobre zonas
        self.canvas.create_line(50, cy, w-50, cy, fill=theme.MUTED)
        for cmark in range(-50, 51, 10):
            xmark = X(cmark)
            color = theme.TEXT if cmark == 0 else theme.MUTED
            self.canvas.create_line(xmark, cy-12, xmark, cy+12, fill=color)
            self.canvas.create_text(xmark, cy+22, text=str(cmark), fill=theme.MUTED)
        # aguja con easing (c ya viene eased desde self._needle_anim)
        c = max(-max_cents, min(max_cents, cents))
        x = X(c)
        self.canvas.create_line(cx, cy-90, x, cy, fill=theme.ACCENT, width=3)
        self.canvas.create_oval(cx-4, cy-4, cx+4, cy+4, fill=theme.ACCENT, outline=theme.ACCENT)
        # punta resplandor
        self.canvas.create_oval(x-6, cy-6, x+6, cy+6, outline=theme.ACCENT, width=1)
        # partículas (sencillas) cuando LED on
        self._update_particles(led_on, x, cy)
        for p in list(self._particles):
            p['y'] -= p['vy']
            p['life'] -= 0.06
            r = p['r']
            if p['life'] <= 0:
                self._particles.remove(p)
                continue
            self.canvas.create_oval(p['x']-r, p['y']-r, p['x']+r, p['y']+r, fill=p['color'], outline="")
        # medidor RMS (barra inferior)
        bar_w = int(min(1.0, max(0.0, rms * 10.0)) * (w - 100))
        self.canvas.create_rectangle(50, h-30, 50 + bar_w, h-18, fill=theme.ACCENT_2, width=0)

    def _refresh_catalog(self) -> None:
        self.catalog = build_catalog()
        self.listbox.delete(0, tk.END)
        for it in self.catalog:
            self.listbox.insert(tk.END, f"{it.title}")
        self._set_status(f"Canciones cargadas: {len(self.catalog)}")

    def _get_selected(self) -> Optional[CatalogItem]:
        try:
            idx = self.listbox.curselection()[0]
        except Exception:
            return None
        return self.catalog[idx]

    def on_analyze(self) -> None:
        item = self._get_selected()
        if not item:
            messagebox.showwarning("Afinador Suno", "Selecciona una canción")
            return
        self._set_status(f"Analizando {item.title} (preciso)...")
        def work():
            try:
                mono = ensure_analysis_mono16k(item.path)
                result = extract_f0_offline(mono, hop_s=0.01, model="full")
                out = ANALYSES_DIR / f"{item.id}.json"
                save_analysis_json(result, out)
                self.analysis_cache[item.id] = out
                self._set_status(f"Listo: {out}")
            except Exception as e:
                self._set_status(f"Error analizando: {e}")
        threading.Thread(target=work, daemon=True).start()

    def on_play(self) -> None:
        item = self._get_selected()
        if not item:
            messagebox.showwarning("Afinador Suno", "Selecciona una canción")
            return
        # No convertir a WAV estéreo: reproducimos directo con ffmpeg stream
        audio_path = item.path

        # cargar análisis si existe o analizar antes si está habilitado
        analysis_path = self.analysis_cache.get(item.id) or (ANALYSES_DIR / f"{item.id}.json")
        analysis = None
        ondemand = None
        if analysis_path.exists():
            analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
        elif self.play_analyze_first.get():
            # Analizar completo en background y luego reproducir
            self._set_status(f"Analizando {item.title} antes de reproducir…")
            def do_analyze_then_play():
                try:
                    mono = ensure_analysis_mono16k(audio_path)
                    res = extract_f0_offline(mono, hop_s=0.02, model="tiny")
                    save_analysis_json(res, analysis_path)
                    self.analysis_cache[item.id] = analysis_path
                except Exception as e:
                    self._set_status(f"Error analizando: {e} (usando on-demand)")
                finally:
                    self.after(0, lambda: self._play_with_analysis(item, audio_path))
            threading.Thread(target=do_analyze_then_play, daemon=True).start()
            return
        else:
            ondemand = OnDemandF0(audio_path, hop_s=0.02, sr=16000, model="tiny")

        # Iniciar micrófono
        def on_frame(frame: PitchFrame) -> None:
            # Calcular datos y guardarlos para que la UI los pinte en el hilo principal
            if frame.voiced:
                name, octave, _ = hz_to_name_and_cents(frame.f0_hz, a4_hz=float(self.a4_hz.get()))
                self._last_ui["me_text"] = f"Tu nota: {name}{octave}"
            else:
                self._last_ui["me_text"] = "Tu nota: -"
            # Voice gating: usar periodicidad, RMS y baseline calibrada
            noise = self.mic.get_noise_rms()
            sens = float(self.sensitivity.get()) / 100.0
            rms_gate = max(0.005, noise * (1.5 + sens * 2.0))
            voice_active = frame.pd >= 0.7 and frame.rms >= rms_gate

            if voice_active and self._last_target_hz > 0:
                # guardar RMS
                self._last_ui["rms"] = frame.rms
                # Auto-octava opcional
                semis_user = float(self.transpose.get())
                best_semis = semis_user
                tgt_base = self._last_target_hz * (2.0 ** (semis_user / 12.0))
                d_base = delta_cents(frame.f0_hz, tgt_base, a4_hz=float(self.a4_hz.get()))
                if self.auto_octave.get():
                    for extra in (-12.0, 12.0):
                        tgt_try = self._last_target_hz * (2.0 ** ((semis_user + extra) / 12.0))
                        d_try = delta_cents(frame.f0_hz, tgt_try, a4_hz=float(self.a4_hz.get()))
                        if abs(d_try) < abs(d_base):
                            d_base = d_try
                            best_semis = semis_user + extra
                    d = d_base
                else:
                    d = d_base
                thr = self._adaptive_threshold_update(d)
                self._last_ui["delta_text"] = f"Δ cents: {d:.1f}"
                self._last_ui["needle"] = d
                good = abs(d) <= thr
                # debounce para LED estable
                self._lock_counter = min(self._lock_counter + 1, 6) if good else max(self._lock_counter - 1, 0)
                self._last_ui["led"] = self._lock_counter >= 2
            else:
                # no voz -> no evaluar afinación
                self._last_ui["delta_text"] = "Δ cents: -"
                self._last_ui["needle"] = 0.0
                self._last_ui["led"] = False
                self._last_ui["rms"] = 0.0
                self._delta_hist.clear()
                self._lock_counter = 0

        self.mic.start(on_frame=on_frame)
        # reset anim
        self._needle_anim = 0.0

        # Iniciar reproducción y, si hay análisis, actualizar objetivo
        offset = float(self.offset_ms.get()) / 1000.0

        def on_pos(t_play: float) -> None:
            if not analysis and ondemand is None:
                self._last_ui["target_text"] = "Objetivo: (sin análisis)"
                self._last_target_hz = 0.0
                return
            if analysis:
                hop = float(analysis.get("hop_s", 0.01))
                idx = int(max(0, (t_play + offset) / hop))
                f0_list = analysis.get("f0_hz", [])
                if idx < len(f0_list):
                    f0_tgt = float(f0_list[idx])
                    self._last_target_hz = f0_tgt if f0_tgt > 0 else 0.0
                    if f0_tgt > 0:
                        name, octv, _ = hz_to_name_and_cents(f0_tgt, a4_hz=float(self.a4_hz.get()))
                        self._last_ui["target_text"] = f"Objetivo: {name}{octv}"
                    else:
                        self._last_ui["target_text"] = "Objetivo: (no vocal)"
                else:
                    self._last_target_hz = 0.0
                    self._last_ui["target_text"] = "Objetivo: (fin)"
            else:
                # On-demand: calcular f0 objetivo en este instante (sin análisis completo)
                f0_tgt = ondemand.f0_at(max(0.0, t_play + offset))
                self._last_target_hz = f0_tgt if f0_tgt > 0 else 0.0
                if f0_tgt > 0:
                    name, octv, _ = hz_to_name_and_cents(f0_tgt, a4_hz=float(self.a4_hz.get()))
                    self._last_ui["target_text"] = f"Objetivo: {name}{octv}"
                else:
                    self._last_ui["target_text"] = "Objetivo: (no vocal)"

        # Si no hay análisis y no pediste analizar primero: reproducir con on-demand
        if not analysis and ondemand is None:
            self.player.play(audio_path, on_position=on_pos)
            self._set_status(f"Reproduciendo: {item.title} (on-demand)")
        else:
            self.player.play(audio_path, on_position=on_pos)
            self._set_status(f"Reproduciendo: {item.title}")

    def on_tuner_classic(self) -> None:
        # Detener reproducción si estaba activa
        try:
            self.player.stop()
        except Exception:
            pass
        self._set_status("Tuner clásico activo (comparación a nota temperada más cercana)")

        def on_frame(frame: PitchFrame) -> None:
            # Gating de voz
            noise = self.mic.get_noise_rms()
            sens = float(self.sensitivity.get()) / 100.0
            rms_gate = max(0.005, noise * (1.5 + sens * 2.0))
            voice_active = frame.pd >= 0.7 and frame.rms >= rms_gate
            if not voice_active:
                self._last_ui["me_text"] = "Tu nota: -"
                self._last_ui["target_text"] = "Objetivo: (sin voz)"
                self._last_ui["delta_text"] = "Δ cents: -"
                self._last_ui["needle"] = 0.0
                self._last_ui["led"] = False
                self._last_ui["rms"] = float(frame.rms)
                self._delta_hist.clear()
                self._lock_counter = 0
                return
            # Nota temperada más cercana
            a4 = float(self.a4_hz.get())
            m = hz_to_midi(frame.f0_hz)
            n = round(m)
            f_ref = midi_to_hz(n, a4_hz=a4)
            # nombres
            name, octv, _ = hz_to_name_and_cents(f_ref, a4_hz=a4)
            # delta en cents
            if f_ref > 0:
                d = 1200.0 * math.log2(frame.f0_hz / f_ref)
            else:
                d = 0.0
            self._last_target_hz = f_ref
            self._last_ui["target_text"] = f"Objetivo: {name}{octv}"
            self._last_ui["me_text"] = f"Tu nota: {name}{octv}"
            thr = self._adaptive_threshold_update(d)
            self._last_ui["delta_text"] = f"Δ cents: {d:.1f}"
            self._last_ui["needle"] = d
            good = abs(d) <= thr
            self._lock_counter = min(self._lock_counter + 1, 6) if good else max(self._lock_counter - 1, 0)
            self._last_ui["led"] = self._lock_counter >= 2
            self._last_ui["rms"] = float(frame.rms)

        self.mic.start(on_frame=on_frame)
        self._needle_anim = 0.0

    def on_analyze_all_fast(self) -> None:
        self.status.configure(text="Analizando todas (rápido)…")
        def work():
            ok, skipped, fail = 0, 0, 0
            for it in self.catalog:
                out = ANALYSES_DIR / f"{it.id}.json"
                if out.exists():
                    skipped += 1
                    continue
                try:
                    stereo, mono = ensure_wav_stereo_and_mono(it.path)
                    res = extract_f0_offline(mono, hop_s=0.02, model="tiny")
                    save_analysis_json(res, out)
                    ok += 1
                    self.analysis_cache[it.id] = out
                except Exception:
                    fail += 1
                self.status.configure(text=f"Progreso: ok={ok} omitidos={skipped} fallidos={fail}")
            self.status.configure(text=f"Análisis masivo terminado: ok={ok}, omitidos={skipped}, fallidos={fail}")
        threading.Thread(target=work, daemon=True).start()

    def on_stop(self) -> None:
        try:
            self.player.stop()
        finally:
            self.mic.stop()
        self._set_status("Detenido")


    def _draw_led(self, good: bool) -> None:
        self.led.delete("all")
        color = theme.SUCCESS if good else theme.DANGER
        # pulso
        t = time.time()
        base_r = 7
        pulse = 2.0 * (0.5 + 0.5 * math.sin(2 * math.pi * (t % 1.0))) if good else 1.0
        r = base_r + (pulse if good else 0)
        # base
        self.led.create_oval(9-base_r, 9-base_r, 9+base_r, 9+base_r, fill=color, outline="")
        # halo
        if good:
            self.led.create_oval(9-r, 9-r, 9+r, 9+r, outline=theme.ACCENT, width=2)

    def _ui_tick(self) -> None:
        # Refrescar UI desde hilo principal (~15-20 fps)
        self.lbl_target.configure(text=self._last_ui.get("target_text", "Objetivo: -"))
        self.lbl_me.configure(text=self._last_ui.get("me_text", "Tu nota: -"))
        self.lbl_delta.configure(text=self._last_ui.get("delta_text", "Δ cents: -"))
        # Easing de aguja
        target = float(self._last_ui.get("needle", 0.0))
        self._needle_anim += (target - self._needle_anim) * 0.2
        led_on = bool(self._last_ui.get("led", False))
        rms = float(self._last_ui.get("rms", 0.0))
        self._draw_needle(self._needle_anim, led_on=led_on, rms=rms)
        self._draw_led(led_on)
        # Modo simple: texto grande
        if self.simple_mode.get():
            led_on = bool(self._last_ui.get("led", False))
            txt = "AFINADO" if led_on else ("SIN VOZ" if self._last_ui.get("delta_text", "-") == "Δ cents: -" else "DESAFINADO")
            self.lbl_state_big.configure(text=txt)
        self.after(self._ui_timer_ms, self._ui_tick)

    def _set_status(self, text: str) -> None:
        self.after(0, lambda: self.status.configure(text=text))

    def _adaptive_threshold_update(self, d: float) -> float:
        # Si no está habilitado, usar el slider
        if not self.auto_threshold.get():
            return float(self.threshold.get())
        # Mantener ventana de ~1.5 s de deltas
        self._delta_hist.append(abs(float(d)))
        if len(self._delta_hist) > 24:
            self._delta_hist = self._delta_hist[-24:]
        if len(self._delta_hist) < 5:
            return 25.0
        arr = np.array(self._delta_hist, dtype=float)
        med = float(np.median(arr))
        mad = float(np.median(np.abs(arr - med)))
        std_approx = 1.4826 * mad
        thr = 2.5 * std_approx
        # límites razonables
        thr = float(np.clip(thr, 12.0, 35.0))
        return thr

    def _update_particles(self, led_on: bool, x: int, y: int) -> None:
        # spawn
        if led_on and len(self._particles) < 40 and random.random() < 0.25:
            self._particles.append({
                'x': x + random.randint(-8, 8),
                'y': y - 10,
                'vy': 2.0 + random.random() * 1.5,
                'r': 2 + random.randint(0, 2),
                'life': 1.0,
                'color': theme.ACCENT,
            })

    def _apply_simple_mode(self) -> None:
        if self.simple_mode.get():
            # Ocultar panel izquierdo y mostrar estado grande
            try:
                self.left.pack_forget()
            except Exception:
                pass
            self.lbl_state_big.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        else:
            # Restaurar panel izquierdo y ocultar estado grande
            try:
                self.left.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=8)
            except Exception:
                pass
            try:
                self.lbl_state_big.pack_forget()
            except Exception:
                pass

    def _start_preanalysis_background(self) -> None:
        def work():
            ok = 0
            limit = int(os.environ.get("AFINADOR_PREANALYZE_LIMIT", "5"))
            for it in self.catalog:
                if limit and ok >= limit:
                    break
                out = ANALYSES_DIR / f"{it.id}.json"
                if out.exists():
                    continue
                try:
                    stereo, mono = ensure_wav_stereo_and_mono(it.path)
                    res = extract_f0_offline(mono, hop_s=0.02, model="tiny")
                    save_analysis_json(res, out)
                    self.analysis_cache[it.id] = out
                    ok += 1
                    self._set_status(f"Pre-analizadas: {ok}")
                except Exception:
                    pass
                time.sleep(0.05)
            if ok:
                self._set_status(f"Pre-analizadas: {ok}")
        threading.Thread(target=work, daemon=True).start()


    def _calibrate_noise(self) -> None:
        val = self.mic.calibrate_noise()
        self._set_status(f"Ruido base: {val:.4f}")


    def _play_with_analysis(self, item: CatalogItem, audio_path: Path) -> None:
        # Reinvocar on_play con análisis ya disponible
        try:
            # simular flujo normal con análisis ya guardado
            self.on_play()
        except Exception:
            # Fallback directo
            self.player.play(audio_path)


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
