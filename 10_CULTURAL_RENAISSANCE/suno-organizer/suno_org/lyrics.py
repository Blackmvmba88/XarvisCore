from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple

from mutagen import File as MutagenFile


def extract_embedded_lyrics(path: Path) -> Optional[str]:
    try:
        m = MutagenFile(path)
        if not m:
            return None
        # MP3 ID3
        if path.suffix.lower() == ".mp3":
            from mutagen.id3 import ID3, USLT
            try:
                tags = ID3(path)
                texts = []
                for frame in tags.getall("USLT"):
                    if getattr(frame, "text", None):
                        texts.append(frame.text)
                if texts:
                    return "\n".join(texts)
            except Exception:
                pass
        # MP4/M4A
        if path.suffix.lower() in {".m4a", ".mp4", ".aac"}:
            try:
                from mutagen.mp4 import MP4
                mp4 = MP4(path)
                if "\xa9lyr" in mp4.tags:
                    vals = mp4.tags.get("\xa9lyr")
                    if isinstance(vals, list) and vals:
                        return str(vals[0])
            except Exception:
                pass
    except Exception:
        return None
    return None


def _has_faster_whisper() -> bool:
    try:
        import faster_whisper  # noqa: F401
        return True
    except Exception:
        return False


def transcribe_excerpt(path: Path, max_duration_sec: int = 45, model_size: str = "small") -> Tuple[Optional[str], Optional[str]]:
    """
    Transcribe first N seconds using faster-whisper if available. Returns (text, error).
    Requires ffmpeg in PATH.
    """
    if not shutil.which("ffmpeg"):
        return None, "ffmpeg not found"
    if not _has_faster_whisper():
        return None, "faster-whisper not installed (pip install faster-whisper)"

    try:
        # Extract mono 16k wav excerpt
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "excerpt.wav"
            cmd = [
                "ffmpeg", "-y", "-i", str(path), "-t", str(max_duration_sec),
                "-ar", "16000", "-ac", "1", "-vn", str(out)
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            from faster_whisper import WhisperModel
            model = WhisperModel(model_size, device="cpu")
            segments, info = model.transcribe(str(out), beam_size=5)
            texts = []
            for seg in segments:
                if getattr(seg, "text", None):
                    texts.append(seg.text.strip())
            txt = " ".join(texts).strip()
            return (txt if txt else None), None
    except Exception as e:
        return None, str(e)


_STOPWORDS_ES = {
    "el","la","los","las","de","del","y","o","u","que","en","un","una","unos","unas","con","por","para","mi","tu","su","te","me","se","lo","le","al","como","si","no","ya","mas","más","muy","es","soy","eres","somos","son","esta","está","estas","estás","estoy","están","quiero","amo","eres","porque","pero","cuando","donde","dónde","a","e","i","o","u"
}
_STOPWORDS_EN = {
    "the","and","a","an","to","of","in","on","for","with","you","me","i","it","is","are","am","be","been","was","were","do","did","does","that","this","these","those","at","as","we","they","he","she","my","your","our","their","but","or","so","if","not"
}


def _tokenize(text: str) -> list[str]:
    text = re.sub(r"[^\w\s'áéíóúñÁÉÍÓÚÑ]", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()
    return text.split()


def suggest_title_from_text(text: str, max_len: int = 48) -> Optional[str]:
    if not text:
        return None
    tokens = [t.lower() for t in _tokenize(text)]
    if not tokens:
        return None
    # Remove stopwords
    tokens_clean = [t for t in tokens if t not in _STOPWORDS_ES and t not in _STOPWORDS_EN]
    # Build n-grams 2..5
    from collections import Counter
    best = None
    for n in range(4, 1, -1):
        grams = [" ".join(tokens_clean[i:i+n]) for i in range(0, max(0, len(tokens_clean)-n+1))]
        grams = [g for g in grams if len(g) >= 6]
        if not grams:
            continue
        c = Counter(grams)
        cand, freq = c.most_common(1)[0]
        if freq >= 2 or best is None:
            best = cand
            if freq >= 2:
                break
    if not best:
        # fallback to first meaningful line
        lines = [ln.strip() for ln in re.split(r"[\r\n]+", text) if ln.strip()]
        if lines:
            best = lines[0]
        else:
            best = "Untitled"
    # Truncate and title-case lightly
    best = best.strip()
    if len(best) > max_len:
        best = best[:max_len].rsplit(" ", 1)[0]
    # Smart title case: capitalize first letters; keep acronyms
    titled = re.sub(r"\b(\w)", lambda m: m.group(1).upper(), best)
    return titled


def lyrics_excerpt(text: Optional[str], max_len: int = 180) -> str:
    if not text:
        return ""
    t = re.sub(r"\s+", " ", text).strip()
    if len(t) <= max_len:
        return t
    return t[:max_len] + "…"