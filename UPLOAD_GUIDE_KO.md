# ToxiGuard NORA v0.9.1 Streamlit 상태 오류 수정 업로드 가이드

## 업로드 대상

이 패치 ZIP에는 GitHub에 올릴 변경 파일만 들어 있습니다.

- `streamlit_app.py`
- `scripts/smoke_streamlit_stub.py`
- `tests/test_navigation_state.py`
- `VALIDATION_REPORT_NAV_STATE_FIX.md`
- `UPLOAD_GUIDE_KO.md`

## GitHub 웹 업로드 순서

1. GitHub 저장소 루트에서 `streamlit_app.py`를 이 패치의 파일로 교체합니다.
2. `scripts/smoke_streamlit_stub.py`를 이 패치의 파일로 교체합니다.
3. `tests/test_navigation_state.py`를 새 파일로 추가합니다.
4. 검증 기록용으로 `VALIDATION_REPORT_NAV_STATE_FIX.md`와 `UPLOAD_GUIDE_KO.md`를 저장소 루트에 추가해도 됩니다.
5. Commit 메시지는 다음처럼 쓰면 됩니다.

```text
Fix Streamlit navigation session_state mutation
```

## 배포 후 확인

Streamlit Cloud가 재배포되면 다음을 확인합니다.

1. 프로젝트 개요 화면이 오류 없이 열리는지 확인합니다.
2. `권장 작업으로 이동` 버튼을 누른 뒤 평가 입력 작업공간으로 이동하는지 확인합니다.
3. 한국어와 English 전환 후에도 같은 버튼 이동이 정상인지 확인합니다.
4. Golden Case 및 컨설팅 사례 불러오기가 프로젝트 상태를 유지하며 평가 입력으로 이동하는지 확인합니다.
5. Evidence Role, Data Gap, 보고서 다운로드 결과가 기존과 같은지 확인합니다.
