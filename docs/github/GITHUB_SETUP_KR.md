# ToxiGuard NORA GitHub 구성 가이드

## 1. 권장 저장소

- Owner: `lyn0109-Toxi`
- Repository: `ToxiGuard-NORA`
- Visibility: 초기에는 **Private 권장**. Streamlit Community Cloud 공개 배포가 필요하면 public 전환을 검토합니다.
- Description: `Ontology-driven evidence assurance for AI/NAM early-toxicity decisions.`
- Topics: `toxicology`, `nam`, `ai`, `ontology`, `streamlit`, `drug-development`, `evidence-assurance`

새 저장소를 만들 때 README, .gitignore, license를 자동 생성하지 마십시오. 이 패키지에 모두 포함되어 있습니다.

## 2. 최초 업로드

```bash
cd ToxiGuard-NORA
./publish_to_github.sh https://github.com/lyn0109-Toxi/ToxiGuard-NORA.git
```

SSH를 사용하는 경우:

```bash
./publish_to_github.sh git@github.com:lyn0109-Toxi/ToxiGuard-NORA.git
```

수동 명령:

```bash
git init
git branch -M main
git add .
git commit -m "Initial release: ToxiGuard NORA EarlyTox v0.4.0"
git remote add origin https://github.com/lyn0109-Toxi/ToxiGuard-NORA.git
git push -u origin main
git tag -a v0.4.0 -m "ToxiGuard NORA EarlyTox v0.4.0"
git push origin v0.4.0
```

## 3. Branch protection

GitHub → Settings → Branches → Add branch protection rule:

- Branch name pattern: `main`
- Require a pull request before merging
- Require approvals: 1
- Dismiss stale approvals after new commits
- Require status checks: `Python 3.11`, `Python 3.12`
- Require conversation resolution
- Block force pushes
- Block deletion

현재 1인 개발 단계에서는 repository owner가 emergency merge를 할 수 있으나, 과학규칙·온톨로지 변경은 Issue와 PR 기록을 남기는 것을 원칙으로 합니다.

## 4. 권장 Labels

```text
area: app
area: evidence
area: ontology
area: rules
area: reports
area: security
type: bug
type: feature
type: science
type: ontology
review: technical
review: scientific
review: ontology
status: triage
status: blocked
status: ready
priority: P0
priority: P1
priority: P2
```

## 5. Streamlit Community Cloud

- Repository: `lyn0109-Toxi/ToxiGuard-NORA`
- Branch: `main`
- Main file: `streamlit_app.py`
- Python: 3.11 또는 3.12
- Secrets: v0.4에는 없음

중요한 프로젝트는 JSON으로 내려받아 보관하십시오. Streamlit Community Cloud 로컬 SQLite는 영구 스토리지로 간주하지 않습니다.

## 6. 첫 Milestone

`NORA v0.5 — Evidence Review Hardening`를 생성하고 `docs/github/ISSUE_BACKLOG_KR.md`의 P0/P1 항목을 Issue로 등록합니다.
