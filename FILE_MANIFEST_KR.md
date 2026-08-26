# ToxiGuard NORA v0.4.0 파일 구성

## 실행
- `streamlit_app.py` — 한국어 Streamlit 앱
- `requirements.txt` — 실행 의존성
- `requirements-dev.txt` — 개발·검증 의존성
- `Dockerfile`, `docker-compose.yml` — 컨테이너 실행

## NORA 엔진
- `nora/models.py` — 구조화 데이터 모델
- `nora/engine.py` — 결정론적 EarlyTox 규칙엔진
- `nora/evidence.py` — PDF/DOCX/XLSX/TXT 근거 추출
- `nora/assertions.py` — Assertion 제안·승인·수정·거절
- `nora/projects.py` — 프로젝트·감사기록 저장
- `nora/ontology.py` — JSON-LD/Turtle 출력
- `nora/reports.py` — 한글 Markdown/PDF/CSV 보고서
- `nora/cases.py` — Golden Case

## TG-PTO-ET
- `ontology/tg_pto_et_core.ttl` — OWL/RDF 의미모델
- `ontology/tg_pto_et_shapes.ttl` — SHACL 검증규칙
- `data/rule_catalog.json` — Evidence Role 결정규칙 목록

## 검증
- `tests/` — 14개 unit/regression test
- `scripts/validate.py` — 통합 release gate
- `scripts/repository_guard.py` — 비밀정보·금지파일·구조 검사
- `scripts/validate_site.py` — 온톨로지 사이트 검증
- `scripts/generate_samples.py` — 결정론적 Golden Case 산출물 재생성
- `.github/workflows/ci.yml` — GitHub Actions CI
- `scripts/configure_github.sh` — Repository topics, labels, milestone 설정

## 사이트
- `site/` — GitHub Pages용 TG-PTO-ET 온톨로지 웹사이트
- `.github/workflows/pages.yml` — Pages 자동배포

## 문서
- `README.md`, `README_KR.md`
- `GOVERNANCE.md`
- `SECURITY.md`
- `ROADMAP.md`
- `docs/` — 제품범위, 아키텍처, Evidence Workflow, 모델카드·NAM 카드 템플릿

## 샘플
- `samples/gp_l_ct/`
- `samples/concordant/`
- `samples/conflict/`

샘플은 모두 가상 또는 비식별 데이터입니다.
