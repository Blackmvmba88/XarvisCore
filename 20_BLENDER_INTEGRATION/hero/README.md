# Hero Mode (GPU) — Overview

This folder contains the initial skeleton for Hero Mode: the high-fidelity GPU-backed rendering pipeline (Cycles + CUDA/Metal/OptiX).

Objectives
- Provide device enumeration and selection utilities for Cycles (CUDA/OPTIX/METAL).
- Provide scheduling and runner topology primitives (single-run and batch modes).
- Provide a safe CI integration plan that gates heavy renders to self-hosted GPU runners.

See the linked issue: https://github.com/Blackmvmba88/XarvisCore/issues/3
