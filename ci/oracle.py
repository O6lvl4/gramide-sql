"""Bounded SQLite syntax comparison; no conformance or checker capability claim."""
from pathlib import Path
import json
import sqlite3
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BIN = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / "gramide_sql"
CASES = json.loads((ROOT / "fixtures/cases.json").read_text())
for filename in CASES["good"]:
    database = sqlite3.connect(":memory:")
    if filename != "schema.sql": database.executescript((ROOT / "fixtures/schema.sql").read_text())
    database.executescript((ROOT / "fixtures" / filename).read_text())
for filename in CASES["bad"]:
    if filename in {"lone_cr.sql", "control_name.sql"}:
        # Intentional pinned-engine coordinate/JSON limitation, valid SQLite syntax.
        sqlite3.connect(":memory:").executescript((ROOT / "fixtures" / filename).read_bytes().decode("utf-8"))
        continue
    database = sqlite3.connect(":memory:")
    database.executescript((ROOT / "fixtures/schema.sql").read_text())
    try: database.executescript((ROOT / "fixtures" / filename).read_text())
    except sqlite3.Error: pass
    else: raise AssertionError(("SQLite accepted negative fixture", filename))

GOOD = [
    "SELECT 1;", "SeLeCt 1;", "SELECT current_time, CURRENT_TIMESTAMP, current_date;",
    "SELECT 1 + 2 * 3, -4, ~1, 0x1f, .5, 1e-2;",
    "SELECT CASE WHEN 1 THEN 'yes' ELSE 'no' END;",
    "SELECT CAST('3' AS INTEGER), coalesce(NULL, 1);",
    "SELECT 2 BETWEEN 1 AND 3, 2 NOT IN (1,3), NULL IS NOT 1;",
    "SELECT 'abc' LIKE 'a%' ESCAPE '!';",
    "VALUES (1,2),(3,4);",
    "SELECT 1 UNION ALL SELECT 2 ORDER BY 1 DESC LIMIT 1;",
    "WITH x(n) AS (VALUES(1)) SELECT n FROM x;",
    'CREATE TABLE "表" ("列" TEXT DEFAULT \'日本語\');',
    "CREATE TABLE t (id INTEGER PRIMARY KEY, value TEXT UNIQUE NOT NULL);",
    "CREATE TABLE t (x INTEGER, y INTEGER GENERATED ALWAYS AS (x+1) STORED);",
    "CREATE TABLE t (id INTEGER PRIMARY KEY) WITHOUT ROWID;",
    "CREATE TABLE t (id INTEGER) STRICT;",
    "CREATE VIEW v AS SELECT 1 AS x;",
    "BEGIN IMMEDIATE;", "SAVEPOINT x;", "PRAGMA user_version = 1;",
]
BAD = [
    "selectx 1;", "SELECT;", "SELECT FROM t;", "SELECT (1;", "SELECT 1 +;",
    "SELECT 1,,2;", "SELECT CASE WHEN 1 THEN END;", "VALUES(1,);",
    "CREATE TABLE t (id INTEGER,);", "CREATE TABLE;", "CREATE VIEW v SELECT 1;",
    "SELECT 'unfinished", "SELECT x'abc';", "SELECT 1e+;", "SELECT /* unfinished",
]
with tempfile.TemporaryDirectory() as temp:
    path = Path(temp) / "oracle.sql"
    for expected, sources in [(True, GOOD), (False, BAD)]:
        for source in sources:
            database = sqlite3.connect(":memory:")
            try: database.execute("EXPLAIN " + source); oracle = True
            except sqlite3.Error: oracle = False
            assert oracle == expected, (source, "fixture expectation mismatches SQLite")
            path.write_text(source)
            result = subprocess.run([str(BIN), "symbols", str(path)], text=True, capture_output=True, timeout=30)
            assert (result.returncode == 0) == oracle, (source, result.stderr)
print(f"SQLite {sqlite3.sqlite_version}: {len(GOOD) + len(BAD)} curated statements plus {len(CASES['good']) + len(CASES['bad']) - 2} files agree; lone-CR/control-name rejection are intentional reader limits")
