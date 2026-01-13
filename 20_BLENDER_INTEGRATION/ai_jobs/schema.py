from typing import Dict, List, Any


class JobValidationError(Exception):
    pass


# Supported step types and minimal required fields per type
_STEP_SPECS = {
    "generate_model": {"required": ["model_name"], "optional": ["parameters"]},
    "apply_materials": {"required": ["target_objects"], "optional": ["materials"]},
    "layout": {"required": ["strategy"], "optional": ["params"]},
    "render_still": {"required": [], "optional": ["camera", "frame", "output", "timeout_seconds"]},
    "render_animation": {"required": ["frame_start", "frame_end", "output_dir"], "optional": ["format"]},
    "export": {"required": ["format", "output_path"], "optional": ["objects", "selected"]},
}


def _is_valid_step(step: Dict[str, Any]) -> List[str]:
    """Return list of validation error messages for a step (empty on success)."""
    errors: List[str] = []
    if not isinstance(step, dict):
        errors.append("step must be an object")
        return errors
    typ = step.get("type")
    if typ not in _STEP_SPECS:
        errors.append(f"unsupported step type: {typ}")
        return errors
    spec = _STEP_SPECS[typ]
    for req in spec["required"]:
        if req not in step:
            errors.append(f"missing required field '{req}' for step type '{typ}'")
    # Basic shallow type checks
    if "target_objects" in step and not isinstance(step.get("target_objects"), list):
        errors.append("target_objects must be a list of object names")
    if "output" in step and not isinstance(step.get("output"), str):
        errors.append("output must be a string file path")
    return errors


def validate_job(job: Dict[str, Any]) -> None:
    """Validate an architect_job spec; raises JobValidationError with details if invalid."""
    errs: List[str] = []
    if not isinstance(job, dict):
        raise JobValidationError("job must be a mapping/object")
    name = job.get("name")
    if not name or not isinstance(name, str):
        errs.append("job.name is required and must be a string")
    steps = job.get("steps")
    if not isinstance(steps, list) or not steps:
        errs.append("job.steps must be a non-empty list")
    else:
        for idx, s in enumerate(steps):
            se = _is_valid_step(s)
            if se:
                errs.extend([f"steps[{idx}]: {m}" for m in se])
    if errs:
        raise JobValidationError("; ".join(errs))
