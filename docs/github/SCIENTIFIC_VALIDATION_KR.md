# 과학적 검증 및 회귀 테스트 기준

## 검증 목적

NORA 검증은 “예측이 맞았다”는 하나의 정확도 시험이 아닙니다. 다음을 각각 확인합니다.

1. 입력 근거가 출처와 연결되는가
2. 누락된 근거가 음성으로 오해되지 않는가
3. 적용범위 밖 결과가 높은 역할을 받지 않는가
4. 방법 신뢰성·후보 적용성·사람 관련성·노출 관련성이 분리되는가
5. 상충근거가 자동으로 평균화되지 않는가
6. R4/R5가 전문가 검토 없이 확정되지 않는가

## Golden cases

| Case | 핵심 조건 | 예상 결과 |
|---|---|---|
| GP-L-CT | 저분자 중심 AI를 siRNA nanomedicine에 적용, 급성 2D NAM, 실제 노출 없음 | R1 이하 |
| Concordant | In-domain AI, 외부검증, 반복 사람 간 모델, 실제 노출, QIVIVE, 독립근거, 전문가 검토 | R4 이상 |
| Conflict | AI 음성, 사람 관련 NAM 양성 | R2 이하, 축소 미지원 |
| Missing QOI | 독성질문 없음 | R0 |

## Rule change acceptance

과학규칙 변경 PR은 최소한 다음을 포함해야 합니다.

- 기존 golden case 결과가 의도 없이 변하지 않음
- 새 규칙의 positive case
- 새 규칙이 발동하지 않아야 하는 negative case
- maximum Evidence Role 검증
- Data Gap ID와 권고문 확인
- 관련 전문영역 검토자 기록

## Expert concordance 계획

파일럿 단계에서는 독성전문가가 동일 사례를 독립적으로 평가한 뒤 다음을 비교합니다.

- 적용범위 판정
- 음성결과 신뢰성
- 주요 Data Gap
- Evidence Role
- 동물시험 관련 권고
- 설명의 명확성

불일치는 오류가 아니라 rule refinement 대상으로 기록합니다.
