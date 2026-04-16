from __future__ import annotations


def validate(input_data: dict, rules: dict | None = None) -> dict:
    rules = rules or {}
    errors: list[str] = []

    if "user_id" not in input_data or not input_data.get("user_id"):
        errors.append("Missing user_id")

    if "action" not in input_data or not input_data.get("action"):
        errors.append("Missing action")

    payload = input_data.get("payload")
    if not isinstance(payload, dict):
        errors.append("payload must be an object")
        payload = {}

    value = payload.get("value")
    if not isinstance(value, (int, float)):
        errors.append("payload.value must be numeric")
    elif value < 0:
        errors.append("Value must be >= 0")

    min_value = rules.get("min_value")
    if min_value is not None and isinstance(value, (int, float)) and value < min_value:
        errors.append(f"Value must be >= {min_value}")

    allowed_actions = rules.get("allowed_actions")
    if allowed_actions and input_data.get("action") not in allowed_actions:
        errors.append("Action not allowed")

    return {"valid": not errors, "errors": errors}
