# Scheduler skeleton for Hero Mode
# Responsibilities:
# - Accept render jobs (single or batch)
# - Assign jobs to available runners
# - Provide dry-run mode for testing without actual GPU resources


class RenderJob:
    def __init__(self, job_id, preset, frames, priority=0):
        self.job_id = job_id
        self.preset = preset
        self.frames = frames
        self.priority = priority


class Scheduler:
    def __init__(self):
        self.queue = []

    def submit(self, job: RenderJob):
        self.queue.append(job)
        return job.job_id

    def dry_run(self):
        # Return a plan without executing; useful for CI.
        return [ (j.job_id, j.preset, j.frames) for j in self.queue ]
