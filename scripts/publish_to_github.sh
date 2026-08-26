#!/usr/bin/env bash
set -euo pipefail

OWNER="${GITHUB_OWNER:-lyn0109-Toxi}"
REPO="${GITHUB_REPO:-ToxiGuard-NORA}"
VISIBILITY="${GITHUB_VISIBILITY:-private}"
REMOTE_URL="${1:-https://github.com/${OWNER}/${REPO}.git}"
VERSION="$(tr -d '[:space:]' < VERSION)"
TAG="v${VERSION}"

python scripts/validate.py

if [ ! -d .git ]; then
  git init -b main
  git add .
  git commit -m "Release ToxiGuard NORA EarlyTox ${TAG}"
fi

git branch -M main

if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  if ! gh repo view "${OWNER}/${REPO}" >/dev/null 2>&1; then
    gh repo create "${OWNER}/${REPO}" --"${VISIBILITY}" \
      --description "Ontology-driven evidence assurance for AI/NAM early-toxicity decisions"
  fi
else
  echo "GitHub CLI가 인증되지 않았습니다. GitHub에서 빈 저장소 ${OWNER}/${REPO}를 먼저 만든 뒤 계속합니다."
fi

if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "${REMOTE_URL}"
else
  git remote add origin "${REMOTE_URL}"
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "커밋되지 않은 변경사항이 있습니다. 먼저 커밋한 뒤 다시 실행하십시오."
  git status --short
  exit 1
fi

if ! git rev-parse "${TAG}" >/dev/null 2>&1; then
  git tag -a "${TAG}" -m "ToxiGuard NORA EarlyTox ${TAG}"
fi

git push -u origin main
git push origin "${TAG}"

if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  ./scripts/configure_github.sh || echo "GitHub metadata/label 설정 일부를 완료하지 못했습니다. 수동 가이드를 확인하십시오."
fi

echo "Published: https://github.com/${OWNER}/${REPO}"
