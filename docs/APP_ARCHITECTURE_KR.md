# NORA EarlyTox v0.4 앱 아키텍처

```text
Streamlit UI
├─ 프로젝트 개요
├─ 문서 근거
├─ Assertion 검토
├─ 구조화 평가 입력
├─ 결과·보고서
└─ 규칙·온톨로지

Document Layer
├─ PDF 페이지
├─ DOCX 문단·표
├─ Excel 시트·행·셀
├─ CSV 행
└─ TXT/JSON 구간

Evidence Layer
DocumentRecord
→ SourceSegment
→ EvidenceAssertion(Proposed)
→ Human Review(Accept/Correct/Reject)
→ AssessmentInput

Decision Layer
AssessmentInput
→ Rule Engine
→ AssessmentResult
├─ 5개 평가축
├─ Hard Gate
├─ Data Gap
├─ Evidence Role R0-R5
└─ Animal-use recommendation

Output Layer
├─ Markdown report
├─ Korean PDF report
├─ JSON-LD
├─ RDF Turtle
├─ Data Gap CSV
└─ Project JSON

Governance Layer
├─ Project ID
├─ Document SHA-256
├─ Source location
├─ Assertion review status
├─ Input hash
├─ Rule/Ontology version
└─ Audit Event
```

## 신뢰 경계

- 문서 추출기는 사실 후보를 제안합니다.
- 승인 전 Assertion은 평가에 사용되지 않습니다.
- LLM 또는 키워드 추출이 Evidence Role을 직접 결정하지 않습니다.
- Rule Engine은 결정론적으로 결과를 생성합니다.
- R4/R5에는 독성전문가 검토가 필요합니다.
