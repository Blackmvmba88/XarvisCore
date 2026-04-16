Scheduler V2 — Diseño para Self-Synthesizing Render Pipelines

Propósito
--------
Definir la arquitectura de scheduling necesaria para habilitar "Style Matching" (imagen → render) mediante un pipeline que aprende: el scheduler deja de ser sólo un asignador de GPU y se convierte en un orquestador cognitivo que programa iteraciones de percepción, síntesis, ejecución, evaluación y aprendizaje.

Core loop
---------
1. Perception (analiza la imagen target)
2. Pipeline Synthesis (genera spec de pipeline ejecutable)
3. Execution (ejecuta pipeline: preview → hero según convergencia)
4. Evaluation (métrica estructural + perceptual, p. ej. SSIM/LPIPS)
5. Learning (ajusta la spec con heurística/optimización o ML)
6. Repetir hasta criterio de parada

Componentes
-----------
- Perception Module: inverse rendering (camera, materials, lighting, style, composition)
- Pipeline Synthesizer: produce PipelineSpec (engine, resolution, passes, denoise, node graphs)
- Execution Engine: asigna recursos, ejecuta (usa Scheduler + device detection)
- Evaluator: métricas de similitud y diagnóstico (cambios por paso)
- Learner: estrategia de búsqueda/optimización (bayesiana, RL, heurística) para actualizar spec

Scheduling dimensions
---------------------
- Recursos: type (CUDA/OPTIX/METAL/CPU), memory, throughput, availability
- Trabajo: job-level (experimento), task-level (pipeline), frame-level (atomic)
- Learning controls: batch size (n pipelines), iterations per job, early-stopping, resume/persist
- Fidelity ladder: preview (low cost) → hero (high cost)

Contracts (qué necesita detection)
----------------------------------
Para cada dispositivo, detection debe proveer como mínimo:
- id (string)
- backend (CUDA|OPTIX|METAL|CPU)
- total_memory_mb, free_memory_mb
- compute_score (0..1 float) — heurístico de capacidad
- optional: temperature_c, occupancy, supported_features, multi_device_group

El scheduler exige también que detección sea consultable con TTL y forzable a refresh bajo demanda.

Heurísticas y políticas
-----------------------
- Admission: aceptar/rechazar trabajos según recursos; fallback CPU si permitido
- Prioritización: buckets (low/normal/high) + deadlines (EDF) + preemption limitada
- Assignment: best-fit(memory + compute_score) combinado con cost model y temperatura
- Batching: agrupar frames/turntables para amortizar setup; multi-GPU split para nodos con NVLink
- Learning scheduling: alternar entre exploración (variante de pipeline) y explotación (mejor spec conocida)

APIs y visibilidad
------------------
- API mínima:
  - submit_experiment(pipeline_seed, target_image, budget)
  - dry_run_experiment(...) → plan
  - get_plan(job_id) → plan JSON
  - get_job_status(job_id)
  - cancel_job(job_id)
- Salidas legibles: plan JSON + tabla Markdown + Gantt (futuro)

Evaluación y criterios de parada
--------------------------------
- Métricas: SSIM, LPIPS, perceptual distance + tareas auxiliares (color histogram, composition match)
- Criterios: alcanzar umbral de similitud, máximo de iteraciones, o presupuesto consumido

Tests y aceptación
------------------
- Unit/smoke:
  - dry_run selecciona dispositivos correctos con mocks
  - planner respeta prioridad y memory constraint
  - learning loop básico mejora métrica en un escenario sintético
- Integration:
  - full end-to-end dry-run: perception->synth->dry_exec->evaluate->learn (no Blender)

Roadmap (próximos PRs)
----------------------
1. Implementar detection fields mínimos (id, backend, memory, compute_score).  
2. Implementar Scheduler.dry_run + unit tests (best-fit + priority + admission).  
3. Implementar experiment job type: seed pipeline + budget + evaluator stub + learning loop (MVP: hill-climb / grid search)
4. Añadir observabilidad: job metrics, device metrics, plan export
5. Integrar con Hero Mode para promociones (preview → hero) y CI gating

Notas finales
------------
Este diseño aterriza la visión: el scheduler orquesta no sólo máquinas sino iteraciones de aprendizaje. Empezamos con dry-run y mocks; una vez establecida la semántica, escalamos a ejecuciones reales en runners GPU.
