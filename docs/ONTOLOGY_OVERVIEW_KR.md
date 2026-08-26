# TG-PTO-ET 온톨로지 개요

## 중심 연결

```text
개발 의사결정
→ 제품 및 노출 맥락
→ 잠재 독성위험
→ 핵심 독성질문
→ Context of Use
→ AI/NAM 방법과 실행
→ Prediction / Observation / Evidence Assertion
→ 방법 신뢰성·후보 적용성·사람 관련성·노출 관련성
→ 근거 일치성과 잔여 불확실성
→ Data Gap
→ Evidence Role R0–R5
→ 3Rs 및 다음 근거 권고
→ 전문가 판단
```

## 핵심 의미제약

```text
Missing evidence ≠ Negative evidence
Negative prediction ≠ Absence of toxicity
Out-of-domain prediction ≠ Reliable evidence
Valid method ≠ Valid execution
Nominal concentration ≠ Target-site exposure
One evidence stream ≠ Weight of evidence
Replacement of one endpoint ≠ Replacement of the toxicology package
```

## 구현 역할 분리

| 계층 | 역할 |
|---|---|
| OWL/RDF | 무엇이 무엇이며 어떻게 연결되는가 |
| SHACL | 필요한 정보가 존재하고 형식이 유효한가 |
| Rule Engine | 어떤 Gate, Gap, Role, 권고가 생성되는가 |
| LLM | 근거 assertion 후보와 설명문을 제안 |
| 전문가 | 고영향 결론을 승인·수정·거절 |
| Audit | 누가 어떤 근거와 버전으로 판단했는가 |
