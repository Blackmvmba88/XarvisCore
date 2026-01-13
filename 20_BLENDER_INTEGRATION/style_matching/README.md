# Style Matching Mode — Image → Render (skeleton)

Purpose
-------
Prototype a pipeline that, given a target image, synthesizes a rendering pipeline that attempts to reproduce the target (Perception → Synthesis → Execution → Evaluation → Learning).

MVP scope (Phase 0):
- Perception mock that extracts simple features from an input image (dominant hue, rough material tags, simple lighting guess)
- PipelineSpec definition (engine, samples, resolution, denoiser, HDRI hint, camera hint)
- Synthesizer that maps perception features -> PipelineSpec (rule-based for MVP)
- Runner dry-run + placeholder evaluation (SSIM or simple pixel distance)

Files in this folder:
- `synthesizer.py` — rule-based synthesizer (skeleton)
- `perception_mock.py` — image->features mock (no ML required for MVP)
- `README.md` — this file

How to contribute
-----------------
1. Start with a small test: `tests/test_style_matching_smoke.py`
2. Implement `perception_mock` and `synthesizer` to satisfy tests
3. Iterate: add a simple evaluator and a small dataset of (target_image, expected_features)

Next steps
----------
- Add smoke tests and CI dry-run similar to preview workflow
- Add a follow-up PR that implements the simplest perception features and a rule-based synthesizer
