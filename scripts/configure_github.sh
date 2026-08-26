#!/usr/bin/env bash
set -euo pipefail

OWNER="${GITHUB_OWNER:-lyn0109-Toxi}"
REPO="${GITHUB_REPO:-ToxiGuard-NORA}"
TARGET="${OWNER}/${REPO}"

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI(gh)가 필요합니다."
  exit 1
fi
if ! gh auth status >/dev/null 2>&1; then
  echo "먼저 'gh auth login'을 실행하십시오."
  exit 1
fi

gh repo edit "${TARGET}" \
  --description "Ontology-driven evidence assurance for AI/NAM early-toxicity decisions" \
  --add-topic toxicology \
  --add-topic nam \
  --add-topic artificial-intelligence \
  --add-topic ontology \
  --add-topic streamlit \
  --add-topic drug-development \
  --add-topic evidence-assurance

while IFS='|' read -r name color description; do
  [ -z "${name}" ] && continue
  gh label create "${name}" --repo "${TARGET}" --color "${color}" --description "${description}" --force
done <<'LABELS'
area: app|1D76DB|Streamlit app and user experience
area: evidence|0E8A16|Evidence extraction, provenance, and assertions
area: ontology|5319E7|TG-PTO-ET ontology and SHACL
area: rules|B60205|Decision rules, gates, and Evidence Role
area: reports|FBCA04|Reports and exports
area: security|D93F0B|Security, privacy, and data governance
type: bug|D73A4A|Defect or regression
type: feature|A2EEEF|Product feature
type: science|C2E0C6|Scientific validation or change
type: ontology|D4C5F9|Semantic model change
review: technical|BFDADC|Technical review required
review: scientific|F9D0C4|Toxicology or scientific review required
review: ontology|E4E669|Ontology governance review required
status: triage|EDEDED|Needs triage
status: blocked|B60205|Blocked by dependency or evidence
status: ready|0E8A16|Ready for implementation or merge
priority: P0|B60205|Critical priority
priority: P1|D93F0B|High priority
priority: P2|FBCA04|Normal priority
bug|D73A4A|Bug report template label
triage|EDEDED|Initial triage
product|1D76DB|Product work
ontology|5319E7|Ontology work
rule-engine|B60205|Decision-rule work
scientific-review|F9D0C4|Scientific review required
validation|0E8A16|Validation work
decision-affecting|D93F0B|May affect a high-impact conclusion
semantic-change|D4C5F9|Changes semantic meaning
enhancement|A2EEEF|Enhancement request
LABELS

if ! gh api "repos/${TARGET}/milestones" --paginate --jq '.[].title' | grep -Fxq 'NORA v0.5 — Evidence Review Hardening'; then
  gh api --method POST "repos/${TARGET}/milestones" \
    -f title='NORA v0.5 — Evidence Review Hardening' \
    -f description='Evidence extraction, assertion review, security, and scientific-validation hardening.' >/dev/null
fi

cat <<MSG
GitHub repository metadata configured: https://github.com/${TARGET}
Next manual settings:
1. Settings → Branches → protect main and require NORA Validation checks.
2. Settings → Pages → Source: GitHub Actions.
3. Settings → Security → enable Dependabot alerts and private vulnerability reporting.
MSG
