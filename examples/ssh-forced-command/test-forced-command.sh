#!/usr/bin/env bash
# Tests for the forced-command wrapper. Stubs out qm/vzdump so the allow-list and
# argument validation can be checked without a hypervisor.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
STUB="$(mktemp -d)"
trap 'rm -rf "$STUB"' EXIT

# Stubs that just echo what they were called with, so we can assert on arguments.
for tool in qm vzdump; do
  { echo '#!/usr/bin/env bash'; echo "echo \"$tool \$*\""; } >"$STUB/$tool"
  chmod +x "$STUB/$tool"
done
export PATH="$STUB:$PATH"

pass=0; fail=0
run() { SSH_ORIGINAL_COMMAND="$1" bash "$HERE/forced-command.sh" 2>/dev/null; }
check() { # name | expected-exit | command
  local name="$1" want="$2" cmd="$3" out rc
  out="$(run "$cmd")"; rc=$?
  if [ "$rc" -eq "$want" ]; then echo "  PASS $name"; pass=$((pass+1));
  else echo "  FAIL $name (exit $rc, wanted $want; out: $out)"; fail=$((fail+1)); fi
}
check_out() { # name | substring | command
  local name="$1" want="$2" cmd="$3" out
  out="$(run "$cmd")"
  if [[ "$out" == *"$want"* ]]; then echo "  PASS $name"; pass=$((pass+1));
  else echo "  FAIL $name (out: $out)"; fail=$((fail+1)); fi
}

echo "== allowed jobs =="
check     "ping is allowed"              0 "ping"
check_out "ping replies pong"            "pong" "ping"
check     "vm-status with a valid id"    0 "vm-status 101"
check_out "vm-status calls qm"           "qm status 101" "vm-status 101"
check_out "backup calls vzdump snapshot" "vzdump 101 --mode snapshot" "backup 101"

echo "== rejected =="
check "unknown job is refused"           1 "rm -rf /"
check "shell metacharacters are data"    1 "vm-status 101; rm -rf /"
check "non-numeric vm id is refused"     1 "vm-status ../etc"
check "empty vm id is refused"           1 "vm-status"
check "extra arguments are refused"      1 "vm-status 101 102"
check "ping rejects an argument"         1 "ping now"
check "an empty request is refused"      1 ""

echo
echo "forced-command: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
