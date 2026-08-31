# ToxiGuard NORA v0.9.1 Navigation State Fix Validation

## 수정 요약

- Streamlit 위젯 키 `nav_page`를 같은 실행 사이클에서 직접 변경하지 않도록 정리했습니다.
- 페이지 이동 버튼은 `pending_nav_page`에 목적지를 저장하고 `st.rerun()`을 요청합니다.
- 다음 실행 시작 시 `pending_nav_page`를 `nav_page`에 반영한 뒤 사이드바 작업공간 위젯을 생성합니다.
- 기존 한글/영문 UI, 프로젝트 상태, Golden Case, 컨설팅 사례, Evidence Role, Data Gap, 보고서 생성 로직은 변경하지 않았습니다.

## 변경 파일

- `streamlit_app.py`
- `scripts/smoke_streamlit_stub.py`
- `tests/test_navigation_state.py`

## 검증 결과

다음 검증을 통과했습니다.

```text
python3 -m py_compile streamlit_app.py scripts/smoke_streamlit_stub.py tests/test_navigation_state.py
python3 -m compileall -q nora scripts tests streamlit_app.py
python3 scripts/smoke_streamlit_stub.py
python3 -m unittest tests.test_navigation_state -v
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -m pytest -q
python3 scripts/validate_compact.py
```

요약:

- Syntax compile: PASS
- Compileall: PASS
- Streamlit smoke runner: PASS, 한국어 및 English 전체 작업공간
- Navigation regression tests: PASS, 3 tests
- Full unittest suite: PASS, 47 tests
- Pytest suite: PASS, 47 passed, 2 subtests passed, 1 rdflib deprecation warning
- Compact package validation: PASS
- Flagship claim audit: PASS

## 회귀 테스트 범위

- 프로젝트 개요의 `권장 작업으로 이동` 버튼이 `nav_page`를 직접 수정하지 않고 `pending_nav_page`를 사용하는지 확인했습니다.
- 다음 rerun에서 `pending_nav_page`가 평가 입력 작업공간으로 반영되는지 확인했습니다.
- 한국어와 English 모두 동일하게 확인했습니다.
- 테스트용 Streamlit stub이 위젯 생성 후 같은 실행 내 widget-bound key 수정 시 `StreamlitAPIException`을 발생시키도록 강화되었습니다.

## 과학 로직 영향

Evidence Role, AI/NAM credibility, Data Gap, ontology, report generation, v0.9.1 case-study data는 수정하지 않았습니다. 기존 엔진, 보고서, 온톨로지, 케이스 검증 테스트가 모두 통과했습니다.
