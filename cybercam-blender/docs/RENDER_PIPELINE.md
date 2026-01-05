# Render Pipeline — cybercam-blender

This document describes the minimal, robust render pipeline used by the project.

Goals
- Produce reproducible, deterministic renders for previews and final outputs.
- Keep rendering lightweight to allow headless CI and local iteration.

What `render_turntable` does
- Renders a sequence of frames (turntable) of the current scene or a specified collection.
- Parameters: frames, resolution, image format, camera name, preset, optional HDRI.
- Output location: `exports/renders/<preset>/frame_0001.png ...`

Presets
- preview (default for quick checks)
  - Engine: Eevee (fast)
  - Samples: low (16)
  - Denoising: off
  - Use case: quick iteration, validation of assembly, and lighting setup.
- final (for production)
  - Engine: Cycles
  - Samples: moderate (128)
  - Denoising: on
  - Use case: production renders, publication.

Lighting
- If an HDRI is provided and final preset requests it, we attach a marker to the world to indicate HDRI should be used (full node wiring is a later task).
- Otherwise a simple 3-point procedural lighting setup is used (implemented inside Blender runtime later).

CLI integration
- `assemble_cam.py --render --render-preset preview` runs assemble then renders the turntable using the preset.
- Additional flags: `--render-frames`, `--render-width`, `--render-height`, `--render-format`, `--render-camera`.

Testing
- Unit tests mock bpy to assert presets are applied and that files are written.
- E2E slow test (gated by `BLENDER_BIN`) runs assemble + render with real Blender and validates PNGs exist and are non-empty.

What we don't do (yet)
- Full HDRI node wiring and advanced compositor nodes (Gamma/contrast presets are annotated but not wired yet).
- Pixel-perfect visual comparisons or aesthetic scoring.

Next steps
- Implement HDRI node wiring and compositing for final preset (requires Blender runtime testing).
- Optionally add presets for 'preview+high-quality' or 'final+ultra' with more granular settings.

