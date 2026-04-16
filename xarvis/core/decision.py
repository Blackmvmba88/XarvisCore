def decide(input_data: dict) -> str:
    payload = input_data.get("payload") or {}
    value = payload.get("value", 0)

    if value > 50:
        return "HIGH"
    if value > 10:
        return "MEDIUM"
    return "LOW"
