# TG-PTO-ET 온톨로지 변경관리

## 원칙

OWL/RDF는 “무엇이 무엇인가”를, SHACL은 “필수 정보가 존재하고 형식이 맞는가”를, Rule Engine은 “현재 근거로 어떤 판단을 할 것인가”를 담당합니다.

## 변경 요청에 필요한 정보

- 클래스/속성/통제어휘/Shape의 IRI
- 한국어 및 영문 label
- 명확한 정의
- 상위클래스 또는 domain/range
- 기존 용어와의 구분
- competency question
- 예시 instance
- backward compatibility 영향
- source 또는 expert rationale

## 버전 규칙

- Patch: label, annotation, 오탈자, 의미 변화 없는 mapping
- Minor: backward-compatible class/property/vocabulary 추가
- Major: 기존 의미 변경, 삭제, cardinality 또는 핵심 constraint 변경

Deprecated term은 즉시 삭제하지 않고 `owl:deprecated true`와 대체 IRI를 제공합니다.

## 검토

- 기술적 RDF/SHACL parsing
- competency question 확인
- 기존 JSON-LD/Turtle export 영향
- rule engine mapping 영향
- scientific reviewer 승인
