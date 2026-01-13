from datetime import timedelta

# Minimum interval between accepted samples for a device
TELEMETRY_MIN_SAMPLE_INTERVAL = timedelta(milliseconds=200)

# Maximum age for a sample to be considered "fresh"
TELEMETRY_TTL = timedelta(milliseconds=800)

# Rolling window for aggregation
TELEMETRY_WINDOW = timedelta(seconds=5)

# Maximum number of samples stored per device
TELEMETRY_MAX_SAMPLES = 64

# Health thresholds (tunable)
GPU_TEMP_WARN = 80.0      # °C
GPU_TEMP_CRIT = 88.0      # °C
GPU_MEM_PRESSURE_WARN = 0.85   # 85% used
GPU_MEM_PRESSURE_CRIT = 0.95   # 95% used

# If no samples in this window, mark stale/offline
STALE_DEVICE_TTL = timedelta(seconds=3)
