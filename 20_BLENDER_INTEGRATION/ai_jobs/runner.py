import os
import time
from typing import Dict, Any, List


class SimulatedRunner:
    """Simulate running architect jobs without Blender.

    Behavior:
      - generate_model: writes a small JSON metadata file to output
      - apply_materials: records materials applied in a log
      - layout: records layout metadata
      - render_still: writes a placeholder image file (binary zeros)
      - render_animation: writes a few placeholder frames
      - export: writes a placeholder export file
    """

    def __init__(self, work_dir: str):
        self.work_dir = os.path.abspath(work_dir)
        os.makedirs(self.work_dir, exist_ok=True)

    def _write_file(self, path: str, data: bytes) -> str:
        full = os.path.join(self.work_dir, path)
        ddir = os.path.dirname(full)
        os.makedirs(ddir, exist_ok=True)
        with open(full, "wb") as f:
            f.write(data)
        return full

    def run(self, job: Dict[str, Any]) -> Dict[str, Any]:
        results: Dict[str, Any] = {"job_name": job.get("name"), "produced": []}
        steps: List[Dict[str, Any]] = job.get("steps", [])
        for idx, step in enumerate(steps):
            typ = step.get("type")
            if typ == "generate_model":
                mn = step.get("model_name")
                fname = f"models/{mn}.json"
                data = ("{\"name\": \"%s\", \"params\": %s}" % (mn, str(step.get("parameters", {})))).encode("utf-8")
                p = self._write_file(fname, data)
                results["produced"].append({"type": "generate_model", "path": p})
            elif typ == "apply_materials":
                fname = f"logs/materials_step_{idx}.txt"
                content = ("Applied %s to %s" % (str(step.get("materials", {})), str(step.get("target_objects", [])))).encode("utf-8")
                p = self._write_file(fname, content)
                results["produced"].append({"type": "apply_materials", "path": p})
            elif typ == "layout":
                fname = f"logs/layout_step_{idx}.json"
                content = ("{\"strategy\": \"%s\", \"params\": %s}" % (step.get("strategy"), str(step.get("params", {})))).encode("utf-8")
                p = self._write_file(fname, content)
                results["produced"].append({"type": "layout", "path": p})
            elif typ == "render_still":
                out = step.get("output") or f"renders/still_{idx}.png"
                # write a tiny fake PNG header + zeros
                data = b"\x89PNG\r\n\x1a\n" + (b"\x00" * 64)
                p = self._write_file(out, data)
                results["produced"].append({"type": "render_still", "path": p})
            elif typ == "render_animation":
                start = int(step.get("frame_start", 1))
                end = int(step.get("frame_end", start))
                outdir = step.get("output_dir") or "renders/anim"
                produced_frames = []
                for f in range(start, end + 1):
                    fname = f"{outdir}/frame_{f:04d}.png"
                    data = b"\x89PNG\r\n\x1a\n" + (b"\x00" * 32)
                    p = self._write_file(fname, data)
                    produced_frames.append(p)
                results["produced"].append({"type": "render_animation", "frames": produced_frames})
            elif typ == "export":
                fmt = step.get("format", "GLTF").lower()
                out = step.get("output_path") or f"export/output.{fmt}".replace("//", "/")
                data = (f"exported {fmt} from job {job.get('name')}").encode("utf-8")
                p = self._write_file(out, data)
                results["produced"].append({"type": "export", "path": p})
            else:
                # unknown step -> record as skipped
                results["produced"].append({"type": "skipped", "step": step})
            # simulate time
            time.sleep(0.01)
        return results
