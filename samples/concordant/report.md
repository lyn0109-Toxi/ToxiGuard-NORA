# ToxiGuard NTR 한글 자문보고서

## 1. 평가 개요

- **프로젝트:** Concordant NTR
- **후보물질:** SM-NME-01
- **제품 Modality:** 저분자 NME
- **평가 목적:** 동물시험 범위 축소 가능성 평가
- **독성 질문:** 검증된 AI 모델과 사람 간 spheroid 음성결과가 저분자 후보의 후속 동물 간독성시험을 정교화하거나 축소하는 데 충분한가?
- **대상 Endpoint:** 초기 간독성
- **현재 Evidence Role:** **R4 — 동물시험 축소 지원**
- **동물사용 관련 권고:** 제한적 축소 지원
- **근거 신뢰도:** 높음
- **독성 신호 방향:** 일관된 음성 신호
- **개별 AI 예측 신뢰성:** 높음
- **개발 우려:** 낮음 — 정의된 Context of Use 내
- **잔여 불확실성:** 낮음
- **모델 위험:** 중간

> 정의된 조건 아래 특정 동물 수·용량군·endpoint 범위 축소를 지원할 수 있습니다.

## 2. AI 독성 신뢰성 프로파일

- **데이터 신뢰성:** 4.0
- **Endpoint·Ground Truth 적절성:** 4.0
- **예측성능 적절성:** 3.8
- **Calibration 적절성:** 4.0
- **개별 예측 신뢰성:** 3.9
- **Lifecycle·Governance:** 4.0

> 모델 전체 성능과 현재 후보에 대한 개별 예측 신뢰성은 다릅니다. Data leakage, 부적절한 ground truth, out-of-domain 사용과 미보정 score는 높은 평균지표로 상쇄되지 않습니다.

## 3. 통합 평가축

- **방법 신뢰성:** 4.0
- **후보 적용성:** 3.5
- **사람 생물학적 관련성:** 4.0
- **노출 관련성:** 4.0
- **근거 일치성:** 3.8
- **잔여 불확실성:** 낮음

## 4. Hard Gate

- **Endpoint·Ground Truth: 통과** — Endpoint 정의, reference standard, label 품질, missing-label 정책을 확인합니다. (낮으면 Evidence Role R2 이하)
- **데이터 독립성·Leakage: 통과** — 학습·시험자료 독립성과 전처리·feature leakage를 확인합니다. (Leakage 또는 비독립 검증은 R1 이하)
- **예측성능·불확실성: 통과** — Sensitivity, specificity, predictive values, threshold, AUPRC 및 confidence interval을 확인합니다. (낮으면 고영향 음성·양성 해석 제한)
- **확률 Calibration: 통과** — 표시된 퍼센트가 calibrated probability인지 확인합니다. (미통과 시 실제 위험확률 표현 금지)
- **개별 예측 신뢰성: 통과** — 현재 후보의 입력품질, domain fit, OOD 및 prediction uncertainty를 확인합니다. (낮으면 Reliable Negative/Positive 불인정)
- **AI Lifecycle·Governance: 통과** — Version, code, data hash, drift monitoring 및 change control을 확인합니다. (낮으면 R4/R5와 반복사용 제한)
- **독성 질문·COU: 통과** — 질문과 제품이 정의되어야 합니다. (미통과 시 R0)
- **방법 식별·버전: 통과** — 정확한 모델/시험법 버전이 필요합니다. (미통과 시 R0 또는 R1)
- **Endpoint 일치: 통과** — 방법 endpoint와 독성질문이 일치해야 합니다. (미통과 시 R0)
- **후보 적용범위: 통과** — AI domain status: In-domain (Out-of-domain 음성은 최대 R1)
- **NAM 실행 유효성: 통과** — 대조군과 실행상태가 유효해야 합니다. (무효 실행은 근거 제외)
- **사람 관련성: 통과** — 관련 세포·대사·면역기능을 확인합니다. (낮으면 R3 이상 제한)
- **노출 번역: 통과** — 실제 노출 및 사람노출 연결이 필요합니다. (낮으면 R3 이상 제한)
- **독립 근거: 통과** — 독립 근거 흐름 7개 (R4/R5에 최소 2개 필요)
- **근거 추적성: 통과** — 문서·페이지·표·원자료로 추적되어야 합니다. (미통과 시 최대 R2)
- **전문가 검토: 통과** — R4/R5에는 독성전문가 승인이 필수입니다. (미검토 시 최대 R3)

## 5. 설명 가능한 자문

### 관찰(Observation)
- 평가 대상은 SM-NME-01이며 제품 modality는 저분자 NME, 투여경로는 경구입니다.
- AI 모델 Validated Hepato-AI v5.2은 음성 / 낮은 위험 예측 결과를 제시했습니다.
- 개별 AI 예측 신뢰성은 높음이며, 데이터·ground truth·성능·calibration·lifecycle을 분리해 평가했습니다.
- 3D 간 Spheroid NAM에서 음성 결과가 입력되었고 노출설계는 반복노출입니다.

### 해석(Interpretation)
- 현재 방법의 신뢰성·적용성·사람 관련성·노출 관련성을 종합하면 다른 독립적 근거와 함께 제한된 범위에서 활용할 수 있습니다.

### 개발상 의미
- 현재 패키지의 Evidence Role은 R4 — 동물시험 축소 지원입니다.
- Evidence Confidence는 높음, Toxicity Direction은 일관된 음성 신호, Development Concern은 낮음 — 정의된 Context of Use 내입니다.
- 명시된 조건과 endpoint에서 동물 수·용량군·중복시험 축소를 검토할 수 있습니다.
- 잔여 불확실성은 낮음이며, 모델 위험은 중간입니다.

### 권고사항
- 현재 근거 역할의 사용조건을 명확히 문서화하고, 실제 동물시험 변경 전 전문가 및 필요 시 규제기관과 검토하십시오.

## 6. 우선순위 Data Gap

- 자동 생성된 주요 Data Gap 없음

## 7. 승인된 Evidence Assertion

- 전문가가 승인한 Evidence Assertion 없음

## 8. 문서 인벤토리

- 업로드 문서 없음

## 9. 감사 추적

- **Assessment ID:** NORA-SAMPLE-CONCORDANT
- **평가 시각(UTC):** 2026-08-26T00:00:00+00:00
- **Ontology:** TG-PTO-ET v0.8
- **Rule Set:** ET + AI Credibility Rules v0.8
- **Input Hash:** a3a3f3894db1383d
- **AI Domain Status:** In-domain
- **Evidence Traceability:** True
- **Assertion Review:** True
- **Expert Review:** True
- **Expert Note:** 제한된 간독성 endpoint에서 용량군과 중복 sampling 축소를 검토할 수 있음.

## 10. 사용 제한

본 결과는 초기 연구 및 의사결정 지원을 위한 규칙기반 prototype 평가입니다. 제품 안전성, 동물시험 면제, 특정 규제기관 수용, CTA/IND 승인 또는 전체 독성시험 대체를 보증하지 않습니다. R4 및 R5의 실제 사용에는 독성전문가 검토와 좁게 정의된 Context of Use가 필요합니다.
