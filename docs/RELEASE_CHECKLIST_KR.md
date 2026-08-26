# NORA Release Checklist

## 코드 및 데이터

- [ ] `python scripts/validate.py` PASS
- [ ] Python 3.11/3.12 CI PASS
- [ ] 프로젝트 schema version 업데이트
- [ ] app/ontology/rule-set version 정합성
- [ ] Golden Case 출력 검토
- [ ] sample report와 ontology output 재생성

## 과학적 검증

- [ ] Missing evidence가 negative evidence로 계산되지 않음
- [ ] Out-of-domain 결과에 보수적 cap 적용
- [ ] Negative result의 exposure/control 조건 확인
- [ ] 독립 근거 흐름 조건 확인
- [ ] R4/R5에 expert-review gate 적용
- [ ] Data Gap과 권고의 rule ID 추적 가능

## 보안 및 운영

- [ ] secret이 저장소에 포함되지 않음
- [ ] confidential sample이 포함되지 않음
- [ ] dependency 및 deployment 검토
- [ ] Streamlit Cloud 또는 Docker smoke test
- [ ] CHANGELOG 업데이트
- [ ] Release notes 작성
