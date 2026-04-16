from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEMO_DIR = ROOT / "examples" / "demo_full"
INPUT_PATH = DEMO_DIR / "input.json"
RULES_PATH = DEMO_DIR / "rules.json"
OUTPUT_PATH = DEMO_DIR / "output.json"
LOG_PATH = ROOT / "logs" / "system.log"
RUNS_DB_PATH = ROOT / "logs" / "runs.sqlite3"
