#!/usr/bin/env bash
# Usage: APP_ID=<github app id> ./apply.sh
set -euo pipefail
: "${APP_ID:?set APP_ID to your test GitHub App's numeric ID}"
REPO="galvana/gitflow-sandbox"
for f in dev-queue release-queue main-protection; do
  tmp=$(mktemp)
  sed "s/APP_ID/$APP_ID/" "$(dirname "$0")/$f.json" > "$tmp"
  gh api "repos/$REPO/rulesets" -X POST --input "$tmp"
  echo "applied $f"
done
