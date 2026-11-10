# ToxiGuard NTR 한글 자문보고서

## 1. 평가 개요

- **프로젝트:** GP-L-CT NTR
- **후보물질:** GP-L-CT
- **제품 Modality:** siRNA + 나노의약품
- **평가 목적:** 동물시험 범위 축소 가능성 평가
- **독성 질문:** 현재 AI와 사람 기반 NAM 근거가 GP-L-CT의 초기 간독성 위험을 평가하고 후속 동물시험 범위를 줄이는 데 충분한가?
- **대상 Endpoint:** 초기 간독성
- **현재 Evidence Role:** **R1 — 가설 생성**
- **동물사용 관련 권고:** 축소·대체 근거 불충분
- **근거 신뢰도:** 낮음
- **독성 신호 방향:** 일관된 음성 신호
- **개별 AI 예측 신뢰성:** 낮음
- **개발 우려:** 미정 — 음성결과만으로 낮게 분류할 수 없음
- **잔여 불확실성:** 매우 높음
- **모델 위험:** 중간

> 잠재 독성위험 또는 기전을 제안하는 수준입니다. 안전성 결론이나 동물시험 축소 근거로 사용할 수 없습니다.

## 2. AI 독성 신뢰성 프로파일

- **데이터 신뢰성:** 1.8
- **Endpoint·Ground Truth 적절성:** 1.5
- **예측성능 적절성:** 1.4
- **Calibration 적절성:** 0.0
- **개별 예측 신뢰성:** 1.1
- **Lifecycle·Governance:** 0.4

> 모델 전체 성능과 현재 후보에 대한 개별 예측 신뢰성은 다릅니다. Data leakage, 부적절한 ground truth, out-of-domain 사용과 미보정 score는 높은 평균지표로 상쇄되지 않습니다.

## 3. 통합 평가축

- **방법 신뢰성:** 2.7
- **후보 적용성:** 1.4
- **사람 생물학적 관련성:** 2.5
- **노출 관련성:** 0.2
- **근거 일치성:** 2.7
- **잔여 불확실성:** 매우 높음

## 4. Hard Gate

- **Endpoint·Ground Truth: 미통과** — Endpoint 정의, reference standard, label 품질, missing-label 정책을 확인합니다. (낮으면 Evidence Role R2 이하)
- **데이터 독립성·Leakage: 조건부** — 학습·시험자료 독립성과 전처리·feature leakage를 확인합니다. (Leakage 또는 비독립 검증은 R1 이하)
- **예측성능·불확실성: 미통과** — Sensitivity, specificity, predictive values, threshold, AUPRC 및 confidence interval을 확인합니다. (낮으면 고영향 음성·양성 해석 제한)
- **확률 Calibration: 미통과** — 표시된 퍼센트가 calibrated probability인지 확인합니다. (미통과 시 실제 위험확률 표현 금지)
- **개별 예측 신뢰성: 미통과** — 현재 후보의 입력품질, domain fit, OOD 및 prediction uncertainty를 확인합니다. (낮으면 Reliable Negative/Positive 불인정)
- **AI Lifecycle·Governance: 미통과** — Version, code, data hash, drift monitoring 및 change control을 확인합니다. (낮으면 R4/R5와 반복사용 제한)
- **독성 질문·COU: 통과** — 질문과 제품이 정의되어야 합니다. (미통과 시 R0)
- **방법 식별·버전: 통과** — 정확한 모델/시험법 버전이 필요합니다. (미통과 시 R0 또는 R1)
- **Endpoint 일치: 통과** — 방법 endpoint와 독성질문이 일치해야 합니다. (미통과 시 R0)
- **후보 적용범위: 미통과** — AI domain status: Out-of-domain (Out-of-domain 음성은 최대 R1)
- **NAM 실행 유효성: 통과** — 대조군과 실행상태가 유효해야 합니다. (무효 실행은 근거 제외)
- **사람 관련성: 통과** — 관련 세포·대사·면역기능을 확인합니다. (낮으면 R3 이상 제한)
- **노출 번역: 조건부** — 실제 노출 및 사람노출 연결이 필요합니다. (낮으면 R3 이상 제한)
- **독립 근거: 통과** — 독립 근거 흐름 4개 (R4/R5에 최소 2개 필요)
- **근거 추적성: 통과** — 문서·페이지·표·원자료로 추적되어야 합니다. (미통과 시 최대 R2)
- **전문가 검토: 미통과** — R4/R5에는 독성전문가 승인이 필수입니다. (미검토 시 최대 R3)

## 5. 설명 가능한 자문

### 관찰(Observation)
- 평가 대상은 GP-L-CT이며 제품 modality는 siRNA + 나노의약품, 투여경로는 정맥투여입니다.
- AI 모델 Small-Molecule Hepato Classifier v3.0은 음성 / 낮은 위험 예측 결과를 제시했습니다.
- 개별 AI 예측 신뢰성은 낮음이며, 데이터·ground truth·성능·calibration·lifecycle을 분리해 평가했습니다.
- 2D 세포시험 NAM에서 음성 결과가 입력되었고 노출설계는 단회/급성 노출입니다.

### 해석(Interpretation)
- AI 모델의 일반적 성능과 별개로 현재 후보는 적용범위 밖이므로 음성예측을 낮은 독성우려로 해석할 수 없습니다.
- 표시된 퍼센트는 calibrated probability로 확인되지 않았으므로 실제 독성 발생확률로 표현할 수 없습니다.
- 실제 free 또는 세포내 노출이 입증되지 않아 NAM 음성결과는 Reliable Negative가 아닙니다.
- 반복 또는 지속 투여계획을 급성 단회 NAM으로만 평가하여 누적·적응·지연독성의 불확실성이 남습니다.

### 개발상 의미
- 현재 패키지의 Evidence Role은 R1 — 가설 생성입니다.
- Evidence Confidence는 낮음, Toxicity Direction은 일관된 음성 신호, Development Concern은 미정 — 음성결과만으로 낮게 분류할 수 없음입니다.
- 추가 근거 확보 전 기존 독성평가를 축소해서는 안 됩니다.
- 잔여 불확실성은 매우 높음이며, 모델 위험은 중간입니다.

### 권고사항
- Carrier-only와 active-only 대조군으로 독성기여를 분리하십시오.
- AI 추출 assertion을 독성전문가가 승인·수정·거절하도록 하십시오.
- 현재 endpoint와 threshold에서 sensitivity, false-negative rate 및 신뢰구간을 확보하십시오.
- 현재 modality를 포함하는 모델 또는 독립적인 orthogonal NAM을 사용하십시오.
- Kupffer cell 공배양, cytokine 또는 보완적인 면역 적격 간 모델을 추가하십시오.
- 예상 사람 Cmax/AUC 또는 초기 PK 가정을 정의하십시오.
- 명목 농도와 별도로 free 또는 세포내 실제 노출을 측정하십시오.
- QIVIVE 또는 PBPK를 이용하여 NAM 농도를 사람노출로 연결하십시오.
- 반복노출 NAM 또는 과학적으로 타당한 acute-to-repeat bridge를 확보하십시오.
- 양성·음성 비율, prevalence 및 imbalance 처리방법을 보고하십시오.
- 화합물, 염, 이성질체, scaffold 및 출처 단위의 중복검사를 수행하십시오.
- 독립 pipeline 기준으로 데이터 누수검사를 수행하고 결과를 보고하십시오.
- 구조 정규화 후 exact duplicate와 scaffold-level overlap을 평가하십시오.
- Blinded expert review, adjudication 또는 label uncertainty 분석을 수행하십시오.
- Missingness taxonomy와 label assignment rule을 문서화하십시오.
- 학습 endpoint의 관찰기간과 현재 Context of Use의 투여기간을 명시하십시오.
- severity/adversity threshold와 판정자를 명시하십시오.
- 해당 endpoint, prevalence 및 threshold에서 FNR과 NPV를 보고하십시오.
- Sensitivity, specificity, PPV/NPV, AUROC/AUPRC에 신뢰구간을 보고하십시오.
- Threshold, 선정목적 및 false-positive/false-negative trade-off를 보고하십시오.
- 외부검증 집단과 현재 후보의 modality, chemical space, endpoint 및 exposure를 비교하십시오.
- 출력값의 정의를 명시하고, 비보정 score에는 확률 또는 confidence라는 표현을 사용하지 마십시오.
- Reliability curve, Brier score, calibration slope/intercept를 제시하십시오.
- Code commit, package/environment lock 및 dataset hash를 함께 기록하십시오.
- Drift trigger, change control, 재검증 기준 및 과거 평가 재실행 절차를 정의하십시오.
- 예측 입력의 identity, structure/sequence normalization 및 batch/formulation 정보를 확인하십시오.
- Nearest-neighbor distance, leverage, domain density 또는 별도 OOD detector를 보고하십시오.
- Prediction explanation을 알려진 독성기전 및 orthogonal NAM endpoint와 연결하십시오.

## 6. 우선순위 Data Gap

- **ET-G025 · Carrier-only 대조군 누락** — 전달체 자체의 독성기여를 분리할 수 없습니다.  
  영향: 제형 기여도 판단 불가  
  권고: Carrier-only와 active-only 대조군으로 독성기여를 분리하십시오.
- **ET-G028 · 구조화 근거 미검토** — AI가 추출한 Evidence Assertion을 전문가가 아직 승인하지 않았습니다.  
  영향: 고영향 결론 보류  
  권고: AI 추출 assertion을 독성전문가가 승인·수정·거절하도록 하십시오.
- **ET-G005 · False-negative 성능 미상** — 음성예측을 고영향 의사결정에 사용하려면 false-negative 특성이 필요합니다.  
  영향: 음성예측의 근거 역할을 R2 이하로 제한할 수 있음  
  권고: 현재 endpoint와 threshold에서 sensitivity, false-negative rate 및 신뢰구간을 확보하십시오.
- **ET-G006 · AI 적용범위 밖** — 현재 후보의 modality 또는 특성이 모델 학습·검증범위에 포함되지 않습니다.  
  영향: 음성예측을 Reliable Negative로 인정하지 않으며 최대 R1  
  권고: 현재 modality를 포함하는 모델 또는 독립적인 orthogonal NAM을 사용하십시오.
- **ET-G016 · 면역·Kupffer cell 반응 미평가** — 나노입자 또는 올리고뉴클레오타이드에서는 간 면역반응의 불확실성이 큽니다.  
  영향: 사람 관련성 및 면역기전 해석 제한  
  권고: Kupffer cell 공배양, cytokine 또는 보완적인 면역 적격 간 모델을 추가하십시오.
- **ET-G018 · 사람 예상노출 정보 부족** — Cmax 또는 AUC가 없어 시험노출과 사람노출을 직접 비교할 수 없습니다.  
  영향: 노출 관련성 제한  
  권고: 예상 사람 Cmax/AUC 또는 초기 PK 가정을 정의하십시오.
- **ET-G019 · 실제 Free/세포내 노출 미측정** — 명목 농도만으로는 세포 또는 표적조직의 실제 노출을 확인할 수 없습니다.  
  영향: 음성 NAM 결과를 Reliable Negative로 인정하지 않음  
  권고: 명목 농도와 별도로 free 또는 세포내 실제 노출을 측정하십시오.
- **ET-G020 · QIVIVE/PBPK 연결 없음** — NAM 결과가 계획된 사람노출로 정량 번역되지 않았습니다.  
  영향: 사람노출 번역 제한  
  권고: QIVIVE 또는 PBPK를 이용하여 NAM 농도를 사람노출로 연결하십시오.
- **ET-G021 · 단회·반복노출 불일치** — 계획된 반복 또는 지속 노출을 급성 단회시험만으로 지원하고 있습니다.  
  영향: 노출 관련성 및 Evidence Role을 R2 이하로 제한할 수 있음  
  권고: 반복노출 NAM 또는 과학적으로 타당한 acute-to-repeat bridge를 확보하십시오.
- **AI-G003 · Class balance 미확인** — 독성 양성 비율과 class imbalance가 보고되지 않았습니다.  
  영향: Accuracy와 AUROC의 해석 제한  
  권고: 양성·음성 비율, prevalence 및 imbalance 처리방법을 보고하십시오.
- **AI-G006 · 시험세트 독립성 불충분** — 학습·튜닝·시험 자료의 독립성과 유사체 중복 여부가 충분히 확인되지 않았습니다.  
  영향: 외부검증 신뢰성 제한  
  권고: 화합물, 염, 이성질체, scaffold 및 출처 단위의 중복검사를 수행하십시오.
- **AI-G008 · Data leakage 평가 불충분** — 전처리, feature selection, 유사체 중복 및 target-derived feature를 포함한 누수평가가 충분하지 않습니다.  
  영향: 모델 성능 과대평가 가능성  
  권고: 독립 pipeline 기준으로 데이터 누수검사를 수행하고 결과를 보고하십시오.
- **AI-G009 · 중복·유사체 평가 불충분** — 동일 화합물, 염, 이성질체 또는 근접 scaffold의 세트 간 중복을 배제하지 못했습니다.  
  영향: 검증성능의 독립성 제한  
  권고: 구조 정규화 후 exact duplicate와 scaffold-level overlap을 평가하십시오.
- **AI-G012 · Label 품질 제한** — 독성 label이 전문가 합의 또는 독립검토를 거쳤다는 근거가 부족합니다.  
  영향: Ground-truth 오류가 모델성능에 전파될 수 있음  
  권고: Blinded expert review, adjudication 또는 label uncertainty 분석을 수행하십시오.
- **AI-G014 · Missing-label 정책 불충분** — 미평가, 결측, 비보고와 실제 음성을 어떻게 구분했는지 충분히 확인되지 않았습니다.  
  영향: 음성 label 신뢰성 제한  
  권고: Missingness taxonomy와 label assignment rule을 문서화하십시오.
- **AI-G015 · 독성 관찰기간 미정의** — 급성, 반복, 지연성 또는 누적 독성 중 어떤 시간범위를 예측하는지 불명확합니다.  
  영향: 현재 투여기간과의 정합성 판단 제한  
  권고: 학습 endpoint의 관찰기간과 현재 Context of Use의 투여기간을 명시하십시오.
- **AI-G016 · 중증도 기준 미정의** — 경미한 변화와 adverse 또는 임상적으로 중대한 독성을 구분하는 기준이 없습니다.  
  영향: 양성예측의 개발상 의미 불명확  
  권고: severity/adversity threshold와 판정자를 명시하십시오.
- **AI-G018 · 음성예측 성능 불충분** — 현재 음성예측을 해석하는 데 필요한 false-negative rate 또는 NPV가 부족합니다.  
  영향: Prediction Reliability 최대 중간  
  권고: 해당 endpoint, prevalence 및 threshold에서 FNR과 NPV를 보고하십시오.
- **AI-G021 · 성능 신뢰구간 미보고** — Point estimate만으로는 모델성능의 통계적 불확실성을 판단할 수 없습니다.  
  영향: 성능추정 정밀도 불명  
  권고: Sensitivity, specificity, PPV/NPV, AUROC/AUPRC에 신뢰구간을 보고하십시오.
- **AI-G022 · Decision threshold 미보고** — 양성·음성을 구분한 threshold와 선택근거가 확인되지 않았습니다.  
  영향: 현재 예측 class의 재현성 제한  
  권고: Threshold, 선정목적 및 false-positive/false-negative trade-off를 보고하십시오.
- **AI-G023 · 외부검증 집단 대표성 불충분** — 외부검증 자료가 현재 modality, endpoint, 노출범위 또는 intended population을 대표하는지 불명확합니다.  
  영향: 현재 Context of Use로의 일반화 제한  
  권고: 외부검증 집단과 현재 후보의 modality, chemical space, endpoint 및 exposure를 비교하십시오.
- **AI-G026 · 출력확률의 의미 불명확** — 화면에 표시된 퍼센트가 calibrated probability인지 원시 score 또는 ensemble agreement인지 불명확합니다.  
  영향: 예측값을 실제 독성확률로 표현할 수 없음  
  권고: 출력값의 정의를 명시하고, 비보정 score에는 확률 또는 confidence라는 표현을 사용하지 마십시오.
- **AI-G027 · Calibration 불충분** — 모델 output과 실제 발생률의 일치가 검증되지 않았습니다.  
  영향: 출력확률을 실제 위험확률로 해석할 수 없음  
  권고: Reliability curve, Brier score, calibration slope/intercept를 제시하십시오.
- **AI-G028 · 재현성 메타데이터 불완전** — Code commit, software environment 또는 training-data hash 중 하나 이상이 없습니다.  
  영향: 동일 예측의 재생산과 변경영향 추적 제한  
  권고: Code commit, package/environment lock 및 dataset hash를 함께 기록하십시오.
- **AI-G029 · Lifecycle·Drift 관리 불충분** — 모델 성능저하, data/concept drift, threshold 변경 및 재검증을 관리하는 절차가 충분하지 않습니다.  
  영향: R4/R5와 장기 운영 적합성 제한  
  권고: Drift trigger, change control, 재검증 기준 및 과거 평가 재실행 절차를 정의하십시오.
- **AI-G030 · 개별 예측 입력 품질 미검증** — 구조, 염형, 이성질체, 서열, 제형 또는 입력 feature가 현재 후보를 정확히 표현하는지 확인되지 않았습니다.  
  영향: 개별 prediction reliability 최대 중간  
  권고: 예측 입력의 identity, structure/sequence normalization 및 batch/formulation 정보를 확인하십시오.
- **AI-G031 · OOD 탐지 근거 부족** — 개별 후보가 학습분포 밖에 있는지 탐지하는 정량적 근거가 부족합니다.  
  영향: Applicability 판단의 객관성 제한  
  권고: Nearest-neighbor distance, leverage, domain density 또는 별도 OOD detector를 보고하십시오.
- **AI-G032 · 생물학적 설명가능성 제한** — 모델이 강조한 feature가 알려진 독성기전, 제품 특성 및 관찰 가능한 endpoint와 충분히 연결되지 않았습니다.  
  영향: 기전적 해석과 후속시험 설계 제한  
  권고: Prediction explanation을 알려진 독성기전 및 orthogonal NAM endpoint와 연결하십시오.

## 7. 승인된 Evidence Assertion

- 전문가가 승인한 Evidence Assertion 없음

## 8. 문서 인벤토리

- 업로드 문서 없음

## 9. 감사 추적

- **Assessment ID:** NORA-SAMPLE-GP-L-CT
- **평가 시각(UTC):** 2026-08-26T00:00:00+00:00
- **Ontology:** TG-PTO-ET v0.8
- **Rule Set:** ET + AI Credibility Rules v0.8
- **Input Hash:** 868be8d7fe5c09e7
- **AI Domain Status:** Out-of-domain
- **Evidence Traceability:** True
- **Assertion Review:** False
- **Expert Review:** False
- **Expert Note:** 없음

## 10. 사용 제한

본 결과는 초기 연구 및 의사결정 지원을 위한 규칙기반 prototype 평가입니다. 제품 안전성, 동물시험 면제, 특정 규제기관 수용, CTA/IND 승인 또는 전체 독성시험 대체를 보증하지 않습니다. R4 및 R5의 실제 사용에는 독성전문가 검토와 좁게 정의된 Context of Use가 필요합니다.
