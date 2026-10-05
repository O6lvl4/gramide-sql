"""Standalone package integration: capabilities, strict symbols and UTF-8 spans."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[1]
LANGUAGE = tomllib.loads((ROOT / 'almide.toml').read_text())['package']['name'].removeprefix('gramide_')
BIN = str(Path(sys.argv[1]).resolve())

def run(command, path=None, *, good=True):
    args = [BIN, command] + ([str(path)] if path is not None else [])
    result = subprocess.run(args, capture_output=True, text=True, timeout=30)
    assert (result.returncode == 0) == good, (args, result.stdout, result.stderr)
    return result

manifest = json.loads(run('languages').stdout)
package, = manifest['packages']
assert package['id'] == LANGUAGE and package['name'] == 'gramide-' + LANGUAGE
assert ("check" in package['capabilities']) == (LANGUAGE == 'json')
assert 'symbols-recovered' not in package['capabilities']
cases = json.loads((ROOT / 'fixtures/cases.json').read_text())
for filename, expected in cases['good'].items():
    path = ROOT / 'fixtures' / filename
    raw = path.read_bytes()
    doc = json.loads(run('symbols', path).stdout)
    assert doc['schema_version'] == 1 and doc['complete'] is True and doc['lang'] == LANGUAGE
    assert set(expected) <= {row['name'] for row in doc['symbols']}
    for row in doc['symbols']:
        lo, hi = row['start_byte'], row['end_byte']
        assert 0 <= lo < hi <= len(raw), row
        assert raw[lo:hi].decode('utf-8').strip(), row
        assert row['start'] == raw[:lo].count(b'\n') + 1, row
        assert 1 <= row['start'] <= row['end'] <= doc['total_lines'], row
    for command in ['parse', 'tokens', 'outline', 'tags']:
        result = run(command, path)
        if command == 'parse': assert 'ERROR' not in result.stdout
    run('check', path, good=LANGUAGE == 'json')
    run('symbols-recovered', path, good=False)
for filename in cases['bad']:
    result = run('symbols', ROOT / 'fixtures' / filename, good=False)
    assert not result.stdout
    if LANGUAGE == 'json': run('check', ROOT / 'fixtures' / filename, good=False)

# The engine uses LF-based document coordinates. Preserve valid CRLF ranges;
# reader-only packages reject lone CR rather than claiming inconsistent output.
original = ROOT / 'fixtures' / next(iter(cases['good']))
raw = original.read_bytes().replace(b'\r\n', b'\n')
assert b'\n' in raw
with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / ('lines' + original.suffix)
    path.write_bytes(raw.replace(b'\n', b'\r\n'))
    doc = json.loads(run('symbols', path).stdout)
    assert doc['total_lines'] == raw.count(b'\n') + (not raw.endswith(b'\n'))
    assert all(1 <= s['start'] <= s['end'] <= doc['total_lines'] for s in doc['symbols'])
    path.write_bytes(raw.replace(b'\n', b'\r'))
    result = run('symbols', path, good=LANGUAGE == 'json')
    if LANGUAGE == 'json':
        doc = json.loads(result.stdout)
        assert doc['total_lines'] == 1
        assert all(s['start'] == s['end'] == 1 for s in doc['symbols'])
    else: assert not result.stdout
print(f'{LANGUAGE}: package contract, {len(cases["good"])} valid/{len(cases["bad"])} malformed files and line-ending ranges passed')
