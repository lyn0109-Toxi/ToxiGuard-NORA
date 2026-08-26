# 배포 안내

## Streamlit Community Cloud

1. GitHub에 `lyn0109-Toxi/ToxiGuard-NORA` 저장소 생성
2. 이 저장소의 `main` 브랜치에 프로젝트 업로드
3. Streamlit Community Cloud에서 **New app** 선택
4. Repository: `lyn0109-Toxi/ToxiGuard-NORA`
5. Branch: `main`
6. Main file: `streamlit_app.py`
7. Python 3.11 또는 3.12
8. Deploy

현재 앱은 외부 API key가 필요하지 않습니다.

## 데이터 보존

- 세션 데이터는 Streamlit 재시작 시 사라질 수 있습니다.
- SQLite는 로컬 파일에 저장되지만 Community Cloud에서는 영구저장으로 간주하면 안 됩니다.
- 중요한 프로젝트는 `.nora.json`으로 내려받아 보관합니다.

## 실사용 전 추가해야 할 것

- 사용자 인증
- 조직/프로젝트별 권한
- 저장 데이터 암호화
- confidential document 분리
- 백업·삭제·보존기간 정책
- immutable audit trail
- 전문가 전자서명
- 규칙 및 온톨로지 release governance
