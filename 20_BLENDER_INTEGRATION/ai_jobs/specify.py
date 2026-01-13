from typing import Dict, Any


def prompt_to_spec(prompt: str) -> Dict[str, Any]:
    """Very small prototype mapping from free text prompt to an `architect_job` spec.

    This is placeholder logic for the prototype. Replace with real LLM calls.
    """
    p = prompt.lower()
    if "studio" in p:
        name = "studio_quick"
        steps = [
            {"type": "generate_model", "model_name": "studio_base", "parameters": {"scale": 1.0}},
            {"type": "layout", "strategy": "simple_grid", "params": {"spacing": 2.0}},
            {"type": "apply_materials", "target_objects": ["wall*", "floor"], "materials": {"wall*": "plaster", "floor": "wood"}},
            {"type": "render_still", "output": "outputs/studio_still.png"},
            {"type": "export", "format": "GLTF", "output_path": "outputs/studio.gltf"},
        ]
    else:
        name = "generic_quick"
        steps = [
            {"type": "generate_model", "model_name": "generic_block", "parameters": {"scale": 1.0}},
            {"type": "render_still", "output": "outputs/generic_still.png"},
        ]
    return {"name": name, "steps": steps}
