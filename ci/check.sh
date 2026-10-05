#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
compiler="${ALMIDE_BIN:-${ALMIDE:-almide}}"
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
"$compiler" check --deny-warnings cli/main.almd
"$compiler" test src/fixture_test.almd
"$compiler" build cli/main.almd --release -o "$work/reader"
"$work/reader" gen-table > "$work/table.almd"
diff -u src/table.almd "$work/table.almd"
python3 ci/package_contract.py "$work/reader"
if [[ -f ci/verify.py ]]; then python3 ci/verify.py "$work/reader"; fi
if [[ -f ci/smoke.py ]]; then python3 ci/smoke.py "$work/reader"; fi
if [[ -f ci/oracle.py ]]; then python3 ci/oracle.py "$work/reader"; fi
