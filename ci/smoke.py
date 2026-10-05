"""Standalone package reader contract: local fixtures, names, spans and gates."""
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
LANGUAGE = "sql"
BIN = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / ("gramide_" + LANGUAGE)

def run(command, path=None, good=True):
    args = [str(BIN), command] + ([str(path)] if path is not None else [])
    result = subprocess.run(args, capture_output=True, text=True, timeout=30)
    assert (result.returncode == 0) == good, (args, result.stdout, result.stderr)
    return result

cases = json.loads((ROOT / "fixtures/cases.json").read_text())
manifest = json.loads(run("languages").stdout)
package, = manifest["packages"]
assert package["id"] == LANGUAGE
assert "check" not in package["capabilities"]
assert "symbols-recovered" not in package["capabilities"]
for filename, expected in cases["good"].items():
    path = ROOT / "fixtures" / filename
    data = path.read_bytes()
    doc = json.loads(run("symbols", path).stdout)
    assert doc["complete"] and doc["schema_version"] == 1
    assert set(expected) <= {row["name"] for row in doc["symbols"]}
    for row in doc["symbols"]:
        lo, hi = row["start_byte"], row["end_byte"]
        assert 0 <= lo < hi <= len(data), row
        assert data[lo:hi].decode("utf-8").strip()
        assert row["start"] == 1 + data[:lo].count(b"\n"), row
    for command in ["tokens", "parse", "outline", "tags"]:
        result = run(command, path)
        if command == "parse": assert "ERROR" not in result.stdout
    run("check", path, good=False)
    run("symbols-recovered", path, good=False)
for filename in cases["bad"]:
    result = run("symbols", ROOT / "fixtures" / filename, good=False)
    assert not result.stdout
print(f"{LANGUAGE}: {len(cases['good'])} positive and {len(cases['bad'])} negative fixtures; command gates and UTF-8 byte spans passed")
