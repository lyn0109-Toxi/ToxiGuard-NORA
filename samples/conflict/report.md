# ToxiGuard NTR 한글 자문보고서

## 1. 평가 개요

- **프로젝트:** Conflicting Evidence NTR
- **후보물질:** Conflict-NME-01
- **제품 Modality:** 저분자 NME
- **평가 목적:** AI·NAM·기존 근거 통합
- **독성 질문:** AI 음성예측과 사람 간 organoid 양성결과가 상충할 때 초기 간독성 위험과 다음 시험을 어떻게 결정해야 하는가?
- **대상 Endpoint:** 초기 간독성
- **현재 Evidence Role:** **R2 — 초기 선별**
- **동물사용 관련 권고:** 축소보다 독성신호 확인 우선
- **근거 신뢰도:** 중간
- **독성 신호 방향:** 상충
- **개별 AI 예측 신뢰성:** 높음
- **개발 우려:** 중간–높음 — 상충 근거 해소 전 낮게 분류 불가
- **잔여 불확실성:** 높음
- **모델 위험:** 높음

> 후보 우선순위와 추가시험 선택에는 사용할 수 있으나, 동물시험 축소·대체를 지지하지 않습니다.

## 2. AI 독성 신뢰성 프로파일

- **데이터 신뢰성:** 4.0
- **Endpoint·Ground Truth 적절성:** 4.0
- **예측성능 적절성:** 3.8
- **Calibration 적절성:** 3.2
- **개별 예측 신뢰성:** 3.6
- **Lifecycle·Governance:** 3.0

> 모델 전체 성능과 현재 후보에 대한 개별 예측 신뢰성은 다릅니다. Data leakage, 부적절한 ground truth, out-of-domain 사용과 미보정 score는 높은 평균지표로 상쇄되지 않습니다.

## 3. 통합 평가축

- **방법 신뢰성:** 3.9
- **후보 적용성:** 3.5
- **사람 생물학적 관련성:** 3.6
- **노출 관련성:** 3.7
- **근거 일치성:** 0.9
- **잔여 불확실성:** 높음

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
- **독립 근거: 통과** — 독립 근거 흐름 4개 (R4/R5에 최소 2개 필요)
- **근거 추적성: 통과** — 문서·페이지·표·원자료로 추적되어야 합니다. (미통과 시 최대 R2)
- **전문가 검토: 미통과** — R4/R5에는 독성전문가 승인이 필수입니다. (미검토 시 최대 R3)

## 5. 설명 가능한 자문

### 관찰(Observation)
- 평가 대상은 Conflict-NME-01이며 제품 modality는 저분자 NME, 투여경로는 경구입니다.
- AI 모델 Hepato-ML v2.1은 음성 / 낮은 위험 예측 결과를 제시했습니다.
- 개별 AI 예측 신뢰성은 높음이며, 데이터·ground truth·성능·calibration·lifecycle을 분리해 평가했습니다.
- 간 Organoid NAM에서 양성 결과가 입력되었고 노출설계는 반복노출입니다.

### 해석(Interpretation)
- AI와 NAM 근거가 상충하므로 어느 결과도 우선하지 않고 원인 규명과 독립적 확인이 필요합니다.

### 개발상 의미
- 현재 패키지의 Evidence Role은 R2 — 초기 선별입니다.
- Evidence Confidence는 중간, Toxicity Direction은 상충, Development Concern은 중간–높음 — 상충 근거 해소 전 낮게 분류 불가입니다.
- 현재 근거는 독성신호의 확인, 기전규명, 노출-반응 및 표적화된 후속시험을 우선하도록 지지합니다. 단순 동물시험 축소로 해석해서는 안 됩니다.
- 잔여 불확실성은 높음이며, 모델 위험은 높음입니다.

### 권고사항
- 상충 원인을 확인할 orthogonal assay와 독립적 전문가 검토를 수행하십시오.

## 6. 우선순위 Data Gap

- **ET-G023 · 근거 간 상충** — AI와 사람 관련 NAM 결과가 반대 방향을 나타냅니다. 원인 규명 전 동물시험 축소를 지지할 수 없습니다.  
  영향: Evidence Role 최대 R2 및 전문가 검토 필요  
  권고: 상충 원인을 확인할 orthogonal assay와 독립적 전문가 검토를 수행하십시오.

## 7. 승인된 Evidence Assertion

- 전문가가 승인한 Evidence Assertion 없음

## 8. 문서 인벤토리

- 업로드 문서 없음

## 9. 감사 추적

- **Assessment ID:** NORA-SAMPLE-CONFLICT
- **평가 시각(UTC):** 2026-08-26T00:00:00+00:00
- **Ontology:** TG-PTO-ET v0.8
- **Rule Set:** ET + AI Credibility Rules v0.8
- **Input Hash:** 6b3386cba26070a2
- **AI Domain Status:** In-domain
- **Evidence Traceability:** True
- **Assertion Review:** True
- **Expert Review:** False
- **Expert Note:** 없음

## 10. 사용 제한

본 결과는 초기 연구 및 의사결정 지원을 위한 규칙기반 prototype 평가입니다. 제품 안전성, 동물시험 면제, 특정 규제기관 수용, CTA/IND 승인 또는 전체 독성시험 대체를 보증하지 않습니다. R4 및 R5의 실제 사용에는 독성전문가 검토와 좁게 정의된 Context of Use가 필요합니다.
