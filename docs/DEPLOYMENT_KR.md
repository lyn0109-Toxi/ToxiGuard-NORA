# 배포 안내

앱의 표시 이름은 **ToxiGuard NTR — Nonclinical Toxicity Review**입니다. 기존 저장소 `lyn0109-Toxi/ToxiGuard-NORA`, 앱 주소 `https://toxiguard-nora.streamlit.app/`, Python 모듈과 환경 변수 이름은 호환성을 위해 유지합니다. NORA는 기존 `/nora` 홈페이지의 통합 작업공간 이름입니다.

이 저장소의 이름 변경을 공개 앱에 반영하려면 배포에 사용하는 브랜치에 변경을 반영하고 Streamlit 재배포 상태를 확인해야 합니다. 로컬 수정만으로 현재 공개 앱이나 별도 NORA 홈페이지가 변경되지는 않습니다.

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
- 중요한 프로젝트는 `.nora.json`으로 내려받아 보관합니다. 기존 `nora-project-*` 프로젝트 형식은 NTR에서도 유지합니다.

## 실사용 전 추가해야 할 것

- 사용자 인증
- 조직/프로젝트별 권한
- 저장 데이터 암호화
- confidential document 분리
- 백업·삭제·보존기간 정책
- immutable audit trail
- 전문가 전자서명
- 규칙 및 온톨로지 release governance
