Hero Mode — Scheduler Design (mini-doc)

Purpose
-------
Define the scheduler contract and design for Hero Mode (GPU-backed Cycles rendering). This document specifies: what we schedule, constraints, heuristics, device metadata contract, outputs, tests, and acceptance criteria. The goal is to make device-detection follow scheduler requirements and to provide a clear, testable contract for execution.

A) What we schedule
--------------------
Granularity levels (supported units):
- Render Job: a logical unit requested by a user/agent (example: "render hero shot mk1"). A job may contain metadata and one or more Tasks.
- Task: a scheduling unit inside a Job, can be one of:
  - "render_still" (single frame)
  - "render_frame_range" (explicit range like start..end)
  - "render_batch" (many independent stills or turntable frames)
  - "export" / "postproc" (GLB export, encoding)
- Frame: atomic rendering unit (lowest unit for parallelization).

Design choices:
- The scheduler treats Tasks as the primary units it assigns to devices; frames inside tasks can be subdivided further for parallel execution when supported by devices.
- Jobs and Tasks carry priority, deadlines (optional), and resource hints (e.g., "requires_gpu": true).

B) Constraints & capabilities
-----------------------------
Metadata we expect from devices (contract):
- backend: {CUDA|OPTIX|METAL|CPU}
- id: unique device identifier
- memory_mb: available device memory (MB)
- free_memory_mb: current free memory (MB) (optional but preferred)
- compute_units: numeric indicator (cores, SMs, etc.) or a heuristic capacity index
- vendor: string (NVIDIA/AMD/Apple/Intel)
- temperature_c: (optional) to support thermal-aware policies
- occupancy_estimate: (optional) estimate of current occupancy (0.0..1.0)
- cost_per_minute: optional cost metric for cloud instances
- multi_device: boolean or integer indicating device is part of a multi-GPU node

Runtime constraints for scheduling decisions:
- memory footprint per Task (hint / estimated): renderer's estimate of memory needed for task.
- time estimate per Task (optional): estimated seconds per frame for a given preset (used by cost heuristic).
- exclusivity flags: some tasks may require exclusive device access (e.g., full-res offline rendering).

C) Heuristics & policies
------------------------
Scheduler policies (configurable and composable):
- Admission policy: reject or queue tasks if required resources are absent (e.g., requires GPU but no GPU nodes available). Optionally allow CPU fallback for non-critical tasks.
- Prioritization:
  - Priority buckets (e.g., low, normal, high)
  - FIFO within same priority unless preemption is required
  - Deadline-aware ordering for urgent jobs (earliest deadline first)
- Assignment heuristic (default): best-fit by memory then compute capacity
  1. Filter devices that satisfy Task's minimal capability constraints (backend, free_memory, multi-device)
  2. Score devices by (free_memory_mb - estimated_task_memory) normalized, combined with compute_units and cost
  3. Prefer device with highest score (best-fit)
- Preemption & eviction: supported only for low-priority background jobs; do not preempt high-priority or exclusive tasks
- Batching & co-scheduling: for small independent frames, pack several frames onto a device to amortize setup cost; use frame-level parallelism for multi-GPU nodes (split frames across devices or use tiled rendering strategies when supported)
- Thermal & reliability: if temperature exceeds a threshold or occupancy too high, gradually shift new tasks to other devices

D) Device-Detection contract (minimal required metadata)
-------------------------------------------------------
The detection component MUST provide (for each reported device):
- id (string)
- backend (string): one of [CUDA, OPTIX, METAL, CPU]
- total_memory_mb (int)
- free_memory_mb (int) OR a reliable way to compute usable memory
- compute_score (float): normalized 0..1 capacity metric (can be derived from cores + clock)

Optional/Recommended fields:
- temperature_c (float)
- occupancy (0..1 float)
- supported_features: list (e.g., ["optix_denoise","out-of-core","rtx" ])
- multi_device_group (string) – devices that should be treated as a group (e.g., NVlink)

Contract notes:
- Detection must be safe to call in non-Blender environments and return a stable empty set.
- Values should be cached with TTL and refreshable on demand from the scheduler.

E) Visualization / outputs
-------------------------
Scheduler should expose a readable plan representation (for both humans and CI):
- Plan JSON example: { job_id, task_id, assigned_device_id, start_estimate, end_estimate, frames: [frame_ranges], priority }
- Human view: simple table (CSV/Markdown)
  | job | task | device | frames | est_secs/frame | priority |
- Timeline / Gantt (future): a timeline view for multi-job runs

F) API / CLI (minimal)
----------------------
- Scheduler API (python):
  - submit_job(job_spec) -> job_id
  - get_plan(job_id) -> JSON plan
  - dry_run(job_spec) -> plan without executing (for CI and validation)
  - cancel(job_id)
  - list_devices() -> device metadata list

- CLI dry-run example:
  python -m hero.scheduler --dry-run --job job.json

G) Tests & acceptance criteria
-----------------------------
Unit/smoke tests to include immediately:
- scheduler.dry_run returns a correct plan structure with mocked devices
- if no devices available and job requires GPU -> dry_run returns rejected state
- best-fit selection: given devices A (small memory), B (big memory) and a task requiring large mem -> scheduler assigns to B
- scheduler.dry_run respects priority ordering

Integration tests (next phase):
- mock device stream that fluctuates free_memory and verify scheduler migrates new jobs to healthy devices
- thermal mock: high temperature leads to non-assignment

H) Metrics & observability
-------------------------
- job wait time distribution
- average assignment decision time (ms)
- device utilization and saturation (by memory & occupancy)
- number of preemptions / cancellations

I) Future extensions (roadmap)
-------------------------------
- Cost-aware scheduling (cloud) and spot preemption strategies
- Batch optimization for multi-GPU nodes (NVLink-aware assignments)
- Per-job quality-of-service levels (e.g., preview vs hero) and artifact promotion workflow (preview artifact validated → schedule hero run)
- ML-assisted estimators for time and memory per task

J) Next steps (concrete)
------------------------
1. Add this SCHEDULER_DESIGN.md to the PR (done).  
2. Implement device detection fields to satisfy contract (device id, backend, total/free memory, compute_score) — small iterative PR.  
3. Implement Scheduler execution for dry-run + unit tests (best-fit and priority).  
4. Add integration tests that mock device churn/thermal and validate policy behavior.  

Acceptance: This doc is accepted when the follow-up PR implements detection and scheduler dry-run code + tests that conform to the contract above.


