# Release draft — v0.3 "Warm-Up"

**Short description (for the top of the GitHub Release page)**

cybercam-blender v0.3 — Warm-Up: a deterministic, testable, headless-first pipeline for assembling and rendering modular assets. Reliability-first: parametric assembly, reproducible preview/final renders, unit tests and gated Blender smoke tests. This was just the warm-up.

---

## Full release notes (GitHub-friendly)

**Title:** v0.3 — Warm-Up

**Overview**

What began as a single camera model has evolved into a deterministic, testable pipeline for assembling and rendering modular objects. This release focuses on making the pipeline reliable, automated, and easy to integrate into CI/workflows — not on visual polish. Visual quality follows once the system is rock-solid.

**Highlights**

- Parametric assembly
  - Anchor-driven assembly & part catalog
  - Screw placement patterns: radial, linear, grid
  - Pure-Python placement utilities with unit tests

- Reproducible rendering
  - Deterministic turntable renderer with stable naming and outputs
  - Render presets: `preview` (Eevee — fast) and `final` (Cycles — denoise, higher samples)
  - Optional HDRI hooks and simple lighting strategy (node wiring planned next)

- CLI-first and headless
  - `assemble_cam.py` + `--render` workflow for headless generation and rendering
  - `20_BLENDER_INTEGRATION/connector.py` + minimal WebUI for orchestration and demos

- Testing & reliability
  - Unit tests for assembler, screw patterns and render presets
  - Gated E2E smoke test (pytest.mark.slow) that runs assemble + render on a real Blender when `BLENDER_BIN` is present
  - CI-safe by default (slow tests are skipped unless Blender is available locally)

- Documentation
  - Quickstart and CLI examples in `README.md`
  - `docs/RENDER_PIPELINE.md` and `docs/STYLE_GUIDE.md` document the pipeline, presets and philosophy

**CLI examples (copy-paste)**

```bash
# generate template parts (if needed)
blender --background --python blend/create_parts_template.py -- --output blend/cybercam_parts.blend

# assemble + preview render (fast)
blender -b blend/cybercam_master.blend --python scripts/build/assemble_cam.py -- --preset mk1 --screws 8 --cables 2 --render --render-preset preview

# assemble + final render (higher quality)
blender -b blend/cybercam_master.blend --python scripts/build/assemble_cam.py -- --preset mk1 --screws 12 --cables 3 --render --render-preset final
```

**What’s next**

- Full HDRI/world node wiring for the `final` preset
- Lightweight compositor nodes (gamma, contrast, denoising refinements)
- Automated variant generation and evaluation

**Philosophy & TL;DR**

Determinism over aesthetics. This release establishes a reliable toolbelt for artists and engineers to iterate fast and programmatically. The visual polish is subsequent work — the foundation is now in place.

---

If you want, I can push this tag and create a GitHub Release draft with the above contents (requires permission). Otherwise it’s ready for you to copy/paste into GitHub when you’re ready to publish.
