# AI Jobs (prototype)

Small prototype utilities for architect_job schema and a simulated runner used for early iterations of the AI→Blender workflow.

Usage examples:

- Validate a job spec:

```py
from ai_jobs import validate_job
validate_job(job)
```

- Run a job (simulation):

```py
from ai_jobs import SimulatedRunner
r = SimulatedRunner(work_dir='/tmp/xarvis-ai')
res = r.run(job)
print(res)
```

- Convert a prompt to a job spec (prototype mapping):

```py
from ai_jobs import specify
job = specify.prompt_to_spec('a cozy studio with lots of light')
```
