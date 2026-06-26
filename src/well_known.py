import json
from pathlib import Path

def get_manifest() -> dict:
    return json.loads((Path(__file__).parent / "static" / "mcp.json").read_text())
