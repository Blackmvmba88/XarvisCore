# CI notes for Hero Mode (GPU)

- Hero Mode jobs should only run on approved self-hosted GPU runners.
- Add a protected workflow `hero-render.yml` that is manual-only and restricted to specific branches or tags.
- Provide a dry-run job in the workflow that validates job composition and artifact promotion without consuming GPUs.
- Define artifact promotion process: preview artifacts are validated and then a human triggers the hero-run which publishes hero artifacts in `exports/hero-renders/`.
