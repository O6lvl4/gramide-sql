# gramide-sql 0.1.0

A separately buildable SQLite-style SQL **structural reader** for gramide v0.2.11.
Original rules based on [SQLite's language documentation](https://www.sqlite.org/lang.html); no upstream parser implementation is copied.

## Supported core

- CREATE TABLE/VIEW/INDEX, column/table constraints, foreign keys, generated columns, ALTER and DROP
- SELECT/VALUES, aliases, joins, WHERE/GROUP/HAVING, compounds, ORDER/LIMIT/OFFSET
- WITH/RECURSIVE CTEs, subqueries, CASE, CAST, EXISTS, operators, IN/BETWEEN/LIKE
- Function calls, FILTER/OVER, named windows and common window frame forms
- INSERT/REPLACE, conflict/upsert clauses, UPDATE, DELETE and RETURNING
- Transactions/savepoints and basic PRAGMA forms
- Case-insensitive ASCII keywords, UTF-8 names, single-quote string doubling, double-quote/backtick/bracket identifiers, blob literals and basic bind parameters

Tables, views, indexes, columns and CTEs are declaration symbols. Quoted names retain their exact quotes/escapes. Qualified names retain their written dots, and columns inside CREATE TABLE are qualified by their table. A query without declarations can correctly produce an empty symbol list.

## Token contract and limits

Supported source line endings are LF and CRLF. Strict scanning rejects lone CR anywhere, including literals/comments, because the pinned engine otherwise gives inconsistent complete symbol line ranges. Byte offsets remain unchanged; recovery uses LF-based source coordinates.

The pinned engine only matches case-sensitive literals and has a fixed token-kind vocabulary. To support `SeLeCt` without altering source bytes, recognized keywords are emitted as one `keyword` token **per ASCII byte**. The grammar matches upper/lower variants of each byte, with longest-first keyword alternatives. Unrecognized words such as `selectx` remain one identifier and cannot match a keyword prefix. Therefore `tokens` exposes a lower-level stream than a conventional SQL lexer, and parse errors may quote a single keyword letter. String/identifier tokens and all byte ranges retain the original source exactly.

This is not SQLite's compiler. Contextual keyword-as-identifier allowances are narrower: quote reserved names. Trigger bodies, virtual-table module argument dialects, ATTACH/DETACH, EXPLAIN, VACUUM, vendor extensions, all PRAGMA variants and every window-frame corner case are not covered. Raw C0 controls other than tab/LF/CRLF are rejected inside bracket/backtick identifiers to protect the pinned engine's JSON symbol output. Schema resolution, aggregate legality, constraint validity and runtime effects are outside scope. Numeric separators and extended Tcl-style bind names are unsupported. No broad upstream conformance corpus has been run.

Capabilities: `tokens`, `parse`, `outline`, `symbols`, `tags`, `map`. No `check` or `symbols-recovered`: strict symbols require a complete parse; recovered outline is best effort.

## Build and validate

```sh
almide test
almide build cli/main.almd -o gramide_sql
./gramide_sql gen-table | diff -u src/table.almd -
./gramide_sql symbols fixtures/schema.sql
python3 ci/oracle.py ./gramide_sql
```

Regenerate with `./gramide_sql gen-table > src/table.almd` after grammar edits, then rebuild. The runtime module imports only this generated table. `src/fixture_test.almd` verifies positive/negative fixtures, names, and dynamic/generated tree equivalence. `ci/check.sh` checks CLI commands, byte ranges and gates. The optional Python sqlite3 oracle checks this fixture set against its installed SQLite version, not arbitrary SQL validity.

## Repository contract

This repository owns this language package and its tests. `src/mod.almd` exports
`definition()` using the shared gramide package API. The `gramide-cli` repository
composes it as a git dependency; no grammar source is vendored into the CLI.
`bash ci/check.sh` runs the complete package gate with an explicit test entry
point, avoiding recursive parallel compiler fan-out. CI pins Almide and Rust
in `.github/workflows/quality.yml`.
