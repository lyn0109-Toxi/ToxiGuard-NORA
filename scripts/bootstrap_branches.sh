#!/usr/bin/env bash
set -euo pipefail

BRANCH="${1:-feature/first-change}"

git checkout main
git pull --ff-only origin main

if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
  git checkout "$BRANCH"
else
  git checkout -b "$BRANCH"
fi

echo "Working branch ready: $BRANCH"
echo "Commit changes, push the branch, and open a Pull Request into main."
