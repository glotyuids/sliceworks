#!/bin/sh
# sliceworks 0.8.1. Money guard (method 16): a Bash command the configuration marks as paid (SW_PAID_CMDS,
# |-separated substrings) is refused when no authorization cap is set, or when the money ledger's total for
# SW_MONEY_CURRENCY has reached SW_MONEY_CAP. Ledger rows: metrics/money.jsonl (schemas/money-entry.schema.json).
input="$(cat)"; . "$(dirname "$0")/lib.sh"; sw_load_config || exit 0
sw_plugin_hooks_enabled || exit 0
[ "$(sw_field '.tool_name')" = "Bash" ] || exit 0
[ -n "$SW_PAID_CMDS" ] || exit 0
cmd="$(sw_field '.tool_input.command')"; [ -n "$cmd" ] || exit 0
hit=0; old_ifs="$IFS"; IFS='|'; for pat in $SW_PAID_CMDS; do case "$cmd" in *"$pat"*) hit=1;; esac; done; IFS="$old_ifs"
[ "$hit" = 1 ] || exit 0
cap="${SW_MONEY_CAP%.*}"
[ "${cap:-0}" -gt 0 ] 2>/dev/null || sw_deny "This command costs money and no authorization is recorded (SW_MONEY_CAP is 0). The owner grants a cap as a D entry; set SW_MONEY_CAP in .sliceworks/config.env, then record each paid run in $SW_MONEY_FILE."
f="$SW_ROOT/$SW_MONEY_FILE"; spent=0
[ -s "$f" ] && spent="$(jq -s --arg c "$SW_MONEY_CURRENCY" '[.[] | select(.currency == $c) | .amount] | add // 0' "$f" 2>/dev/null || echo 0)"
if [ "$(printf '%s >= %s\n' "$spent" "$SW_MONEY_CAP" | bc 2>/dev/null || echo 0)" = 1 ]; then
  sw_deny "Money cap reached: ${spent} ${SW_MONEY_CURRENCY} spent of ${SW_MONEY_CAP} ${SW_MONEY_CURRENCY} authorized ($SW_MONEY_FILE). Raising the cap is a human-only act (method 10); ask through NEEDS-HUMAN.md."
fi
exit 0
