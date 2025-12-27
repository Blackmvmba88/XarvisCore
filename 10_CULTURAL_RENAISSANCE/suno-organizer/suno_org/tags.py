from __future__ import annotations

from pathlib import Path
from typing import Optional

from mutagen import File as MutagenFile


def write_tags(
    path: Path,
    title: Optional[str] = None,
    artist: Optional[str] = None,
    album: Optional[str] = None,
    genre: Optional[str] = None,
    lyrics: Optional[str] = None,
    cover_image_path: Optional[Path] = None,
) -> bool:
    ext = path.suffix.lower()
    try:
        if ext == ".mp3":
            from mutagen.id3 import ID3, TIT2, TPE1, TALB, TCON, USLT, APIC, ID3NoHeaderError
            try:
                tags = ID3(path)
            except ID3NoHeaderError:
                from mutagen.id3 import ID3
                tags = ID3()
            if title is not None:
                tags.setall("TIT2", [TIT2(encoding=3, text=title)])
            if artist is not None:
                tags.setall("TPE1", [TPE1(encoding=3, text=artist)])
            if album is not None:
                tags.setall("TALB", [TALB(encoding=3, text=album)])
            if genre is not None:
                tags.setall("TCON", [TCON(encoding=3, text=genre)])
            if lyrics is not None:
                tags.setall("USLT", [USLT(encoding=3, lang='spa', desc='Lyrics', text=lyrics)])
            if cover_image_path and cover_image_path.exists():
                img = cover_image_path.read_bytes()
                tags.setall("APIC", [APIC(encoding=3, mime='image/jpeg', type=3, desc='Cover', data=img)])
            tags.save(path)
            return True
        elif ext in {".m4a", ".mp4", ".aac"}:
            from mutagen.mp4 import MP4, MP4Cover
            mp4 = MP4(path)
            if title is not None:
                mp4["\xa9nam"] = [title]
            if artist is not None:
                mp4["\xa9ART"] = [artist]
            if album is not None:
                mp4["\xa9alb"] = [album]
            if genre is not None:
                mp4["\xa9gen"] = [genre]
            if lyrics is not None:
                mp4["\xa9lyr"] = [lyrics]
            if cover_image_path and cover_image_path.exists():
                data = cover_image_path.read_bytes()
                mp4['covr'] = [MP4Cover(data, imageformat=MP4Cover.FORMAT_JPEG)]
            mp4.save()
            return True
        else:
            # Try generic tags
            m = MutagenFile(path, easy=True)
            if not m:
                return False
            if title is not None:
                m["title"] = title
            if artist is not None:
                m["artist"] = artist
            if album is not None:
                m["album"] = album
            if genre is not None:
                m["genre"] = genre
            m.save()
            return True
    except Exception:
        return False
