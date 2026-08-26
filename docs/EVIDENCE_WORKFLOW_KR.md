# NORA EarlyTox Evidence Workflow

## 1. 기본 원칙

```text
문서가 존재한다
≠ 독성질문에 답한다
≠ 신뢰 가능한 근거이다
≠ 현재 후보에 적용 가능하다
≠ 사람노출에서 안전하다
```

## 2. 문서에서 판단까지

1. EvidenceItem: 보고서·논문·표·원자료
2. SourceSegment: 페이지·문단·시트·행 단위 근거구간
3. EvidenceAssertion: `주어-관계-값` 형식의 구조화 후보
4. Human Review: 승인·수정·거절
5. AssessmentInput: 승인된 값과 수동 검토값의 통합
6. SHACL/Rule Validation: 필수정보·적용범위·대조군·노출 검증
7. AssessmentResult: 평가축, Hard Gate, Data Gap, Evidence Role
8. Human Expert Decision: R4/R5 및 예외 판단

## 3. Assertion 예시

```text
Assertion ID: AST-001
Field: ai_model.false_negative_rate_percent
Value: 10
Source: Model_Validation_Report.pdf
Location: PDF 14페이지
Review Status: 승인
```

## 4. 평가에 사용되는 상태

- 승인
- 수정

`제안됨`과 `거절`은 평가 입력에 반영하지 않습니다.

## 5. Negative 결과의 최소 조건

AI 음성예측:

- Endpoint 일치
- Applicability domain
- 독립 검증
- Sensitivity와 false-negative 성능
- 정확한 모델 버전

NAM 음성결과:

- 유효한 양성·음성대조군
- 충분한 실제 표적노출
- 적절한 endpoint
- 반복노출 정합성
- 사람 관련 생물학
- 시험물질/전달체 대조군
