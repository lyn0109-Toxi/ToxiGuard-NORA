# ToxiGuard NORA EarlyTox 한글 자문보고서

## 1. 평가 개요

- **프로젝트:** GP-L-CT EarlyTox
- **후보물질:** GP-L-CT
- **제품 Modality:** siRNA + 나노의약품
- **평가 목적:** 동물시험 범위 축소 가능성 평가
- **독성 질문:** 현재 AI와 사람 기반 NAM 근거가 GP-L-CT의 초기 간독성 위험을 평가하고 후속 동물시험 범위를 줄이는 데 충분한가?
- **대상 Endpoint:** 초기 간독성
- **현재 Evidence Role:** **R1 - 가설 생성**
- **동물사용 관련 권고:** 축소·대체 근거 불충분
- **잔여 불확실성:** 매우 높음
- **모델 위험:** 중간

> 잠재 독성위험 또는 기전을 제안하는 수준입니다. 안전성 결론이나 동물시험 축소 근거로 사용할 수 없습니다.

## 2. 평가축

- **방법 신뢰성:** 2.7
- **후보 적용성:** 1.4
- **사람 생물학적 관련성:** 2.5
- **노출 관련성:** 0.2
- **근거 일치성:** 2.7
- **잔여 불확실성:** 매우 높음

## 3. Hard Gate

- **독성 질문·COU: 통과** - 질문과 제품이 정의되어야 합니다. (미통과 시 R0)
- **방법 식별·버전: 통과** - 정확한 모델/시험법 버전이 필요합니다. (미통과 시 R0 또는 R1)
- **Endpoint 일치: 통과** - 방법 endpoint와 독성질문이 일치해야 합니다. (미통과 시 R0)
- **후보 적용범위: 미통과** - AI domain status: Out-of-domain (Out-of-domain 음성은 최대 R1)
- **NAM 실행 유효성: 통과** - 대조군과 실행상태가 유효해야 합니다. (무효 실행은 근거 제외)
- **사람 관련성: 통과** - 관련 세포·대사·면역기능을 확인합니다. (낮으면 R3 이상 제한)
- **노출 번역: 조건부** - 실제 노출 및 사람노출 연결이 필요합니다. (낮으면 R3 이상 제한)
- **독립 근거: 통과** - 독립 근거 흐름 4개 (R4/R5에 최소 2개 필요)
- **근거 추적성: 통과** - 문서·페이지·표·원자료로 추적되어야 합니다. (미통과 시 최대 R2)
- **전문가 검토: 미통과** - R4/R5에는 독성전문가 승인이 필수입니다. (미검토 시 최대 R3)

## 4. 설명 가능한 자문

### 관찰(Observation)
- 평가 대상은 GP-L-CT이며 제품 modality는 siRNA + 나노의약품, 투여경로는 정맥투여입니다.
- AI 모델 Small-Molecule Hepato Classifier v3.0은 음성 / 낮은 위험 예측 결과를 제시했습니다.
- 2D 세포시험 NAM에서 음성 결과가 입력되었고 노출설계는 단회/급성 노출입니다.

### 해석(Interpretation)
- AI 모델의 일반적 성능과 별개로 현재 후보는 적용범위 밖이므로 음성예측을 낮은 독성우려로 해석할 수 없습니다.
- 실제 free 또는 세포내 노출이 입증되지 않아 NAM 음성결과는 Reliable Negative가 아닙니다.
- 반복 또는 지속 투여계획을 급성 단회 NAM으로만 평가하여 누적·적응·지연독성의 불확실성이 남습니다.

### 개발상 의미
- 현재 패키지의 Evidence Role은 R1 — 가설 생성입니다.
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

## 5. 우선순위 Data Gap

- **ET-G025 · Carrier-only 대조군 누락** - 전달체 자체의 독성기여를 분리할 수 없습니다.  
  영향: 제형 기여도 판단 불가  
  권고: Carrier-only와 active-only 대조군으로 독성기여를 분리하십시오.
- **ET-G028 · 구조화 근거 미검토** - AI가 추출한 Evidence Assertion을 전문가가 아직 승인하지 않았습니다.  
  영향: 고영향 결론 보류  
  권고: AI 추출 assertion을 독성전문가가 승인·수정·거절하도록 하십시오.
- **ET-G005 · False-negative 성능 미상** - 음성예측을 고영향 의사결정에 사용하려면 false-negative 특성이 필요합니다.  
  영향: 음성예측의 근거 역할을 R2 이하로 제한할 수 있음  
  권고: 현재 endpoint와 threshold에서 sensitivity, false-negative rate 및 신뢰구간을 확보하십시오.
- **ET-G006 · AI 적용범위 밖** - 현재 후보의 modality 또는 특성이 모델 학습·검증범위에 포함되지 않습니다.  
  영향: 음성예측을 Reliable Negative로 인정하지 않으며 최대 R1  
  권고: 현재 modality를 포함하는 모델 또는 독립적인 orthogonal NAM을 사용하십시오.
- **ET-G016 · 면역·Kupffer cell 반응 미평가** - 나노입자 또는 올리고뉴클레오타이드에서는 간 면역반응의 불확실성이 큽니다.  
  영향: 사람 관련성 및 면역기전 해석 제한  
  권고: Kupffer cell 공배양, cytokine 또는 보완적인 면역 적격 간 모델을 추가하십시오.
- **ET-G018 · 사람 예상노출 정보 부족** - Cmax 또는 AUC가 없어 시험노출과 사람노출을 직접 비교할 수 없습니다.  
  영향: 노출 관련성 제한  
  권고: 예상 사람 Cmax/AUC 또는 초기 PK 가정을 정의하십시오.
- **ET-G019 · 실제 Free/세포내 노출 미측정** - 명목 농도만으로는 세포 또는 표적조직의 실제 노출을 확인할 수 없습니다.  
  영향: 음성 NAM 결과를 Reliable Negative로 인정하지 않음  
  권고: 명목 농도와 별도로 free 또는 세포내 실제 노출을 측정하십시오.
- **ET-G020 · QIVIVE/PBPK 연결 없음** - NAM 결과가 계획된 사람노출로 정량 번역되지 않았습니다.  
  영향: 사람노출 번역 제한  
  권고: QIVIVE 또는 PBPK를 이용하여 NAM 농도를 사람노출로 연결하십시오.
- **ET-G021 · 단회·반복노출 불일치** - 계획된 반복 또는 지속 노출을 급성 단회시험만으로 지원하고 있습니다.  
  영향: 노출 관련성 및 Evidence Role을 R2 이하로 제한할 수 있음  
  권고: 반복노출 NAM 또는 과학적으로 타당한 acute-to-repeat bridge를 확보하십시오.

## 6. 승인된 Evidence Assertion

- 전문가가 승인한 Evidence Assertion 없음

## 7. 문서 인벤토리

- 업로드 문서 없음

## 8. 감사 추적

- **Assessment ID:** NORA-SAMPLE-GP-L-CT
- **평가 시각(UTC):** 2026-08-26T00:00:00+00:00
- **Ontology:** TG-PTO-ET v0.4
- **Rule Set:** ET Rules v0.4
- **Input Hash:** 11cf913fc9a948dc
- **AI Domain Status:** Out-of-domain
- **Evidence Traceability:** True
- **Assertion Review:** False
- **Expert Review:** False
- **Expert Note:** 없음

## 9. 사용 제한

본 결과는 초기 연구 및 의사결정 지원을 위한 규칙기반 prototype 평가입니다. 제품 안전성, 동물시험 면제, 특정 규제기관 수용, CTA/IND 승인 또는 전체 독성시험 대체를 보증하지 않습니다. R4 및 R5의 실제 사용에는 독성전문가 검토와 좁게 정의된 Context of Use가 필요합니다.
