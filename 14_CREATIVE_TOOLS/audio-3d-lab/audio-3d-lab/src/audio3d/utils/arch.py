import platform

def detect_arch():
    m = platform.machine().lower()
    if "arm" in m or "aarch64" in m:
        return "arm64 (Apple Silicon)"
    if "x86_64" in m or "amd64" in m:
        return "x86_64 (Intel)"
    return m
