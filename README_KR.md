# ToxiGuard NORA EarlyTox v0.4

## 1. 제품 정의

**ToxiGuard NORA**는 `Nonclinical Ontology-based Risk Advisor`의 약자입니다.

NORA EarlyTox는 AI와 비동물시험법(NAM)이 생성한 초기 독성근거를 그대로 안전성 결론으로 사용하지 않고 다음 질문에 답합니다.

> 이 근거는 어떤 독성질문에서, 어떤 Context of Use 아래, 현재 후보물질의 개발에 어디까지 사용할 수 있는가?

NORA는 독성 예측모델 자체가 아니라 **독성근거의 신뢰성·후보 적용성·사람 생물학적 관련성·노출 관련성·근거 일치성·잔여 불확실성을 검증하는 Evidence Assurance 작업공간**입니다.

## 2. 핵심 작동 구조

```text
문서 업로드
→ 페이지·문단·시트·행 기반 근거 추출
→ Evidence Assertion 후보 생성
→ 사람이 승인·수정·거절
→ 승인된 Assertion만 평가 입력에 반영
→ SHACL 구조 검증
→ 결정론적 Rule Engine
→ Evidence Role R0–R5
→ 한글 자문·PDF·JSON-LD·Turtle·CSV
→ 프로젝트 및 Audit 저장
```

AI가 제안한 값은 기본적으로 `제안됨` 상태이며, 사람의 검토 없이는 고영향 판단에 사용하지 않습니다.

## 3. 현재 활성 과학 범위

- Endpoint: 초기 간독성
- Modality: 저분자, 올리고뉴클레오타이드, siRNA, 나노의약품, 바이오의약품, 유전자치료제
- 방법: AI/QSAR, 2D 사람 간세포, coculture, spheroid, organoid, liver-on-chip/MPS
- 출력: Evidence Role R0–R5, 동물사용 관련 권고, Hard Gate, Data Gap, 다음 근거

다른 endpoint는 구조상 확장할 수 있지만, v0.4의 상세 결정규칙은 초기 간독성 vertical slice에 집중합니다.

## 4. Evidence Role

| Role | 의미 |
|---|---|
| R0 | 평가 불가 |
| R1 | 가설 생성 |
| R2 | 초기 선별 |
| R3 | 보조 근거 |
| R4 | 동물시험 축소 지원 |
| R5 | 특정 시험·endpoint 대체 후보 |

R5도 동물시험 면제, 규제기관 수용, 제품 안전성 인증 또는 전체 독성패키지 대체를 의미하지 않습니다.

## 5. 실행

```bash
git clone https://github.com/lyn0109-Toxi/ToxiGuard-NORA.git
cd ToxiGuard-NORA
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

또는:

```bash
make install
make run
```

## 6. GitHub 운영방식

- `main`: 검증을 통과한 배포 가능 코드
- `feature/*`: 기능 개발
- `science/*`: 독성 규칙·온톨로지 변경
- `fix/*`: 버그 수정
- 릴리스는 검증된 `main` 커밋에 `vX.Y.Z` 태그를 부여합니다.

과학적 규칙, Evidence Role 또는 온톨로지 변경은 반드시 다음을 포함합니다.

1. 변경 이유와 Context of Use
2. 규칙 ID 또는 클래스/속성 ID
3. Golden Case 영향
4. 회귀 테스트
5. 독성전문가 검토 필요 여부

자세한 내용은 [`docs/GITHUB_WORKFLOW_KR.md`](docs/GITHUB_WORKFLOW_KR.md)를 확인하십시오. 원격 저장소 생성 후 `scripts/configure_github.sh`를 실행하면 topics, labels, milestone을 자동 구성할 수 있습니다.

## 7. Streamlit Community Cloud

- Repository: `lyn0109-Toxi/ToxiGuard-NORA`
- Branch: `main`
- Main file path: `streamlit_app.py`
- Python: 3.11 또는 3.12
- Secrets: 현재 v0.4는 필수 secret 없음

프로젝트의 SQLite 저장소는 Cloud에서 영구저장으로 간주하지 않고, `.nora.json` 백업을 권장합니다.

## 8. Docker

```bash
docker compose up --build
```

브라우저에서 `http://localhost:8501`을 엽니다.

## 9. 검증

```bash
python scripts/generate_samples.py  # Golden Case 산출물 재생성
python scripts/validate.py          # 통합 Release Gate
```

회귀검증 범위:

- GP-L-CT: R1 이하
- 고품질 일치 사례: R4 이상
- AI/NAM 상충 사례: R2 이하
- 독성질문 누락: R0
- TXT/DOCX/PDF/XLSX 추출
- Assertion 추출 및 승인값 적용
- SQLite 프로젝트 저장·불러오기·삭제
- 한글 Markdown/PDF 생성
- JSON-LD/Turtle 생성
- OWL/RDF 및 SHACL TTL 파싱

## 10. 중요한 제한

- 초기 연구 및 의사결정 지원용 prototype입니다.
- 제품 안전성을 인증하지 않습니다.
- 동물시험 면제 또는 규제기관 수용을 보장하지 않습니다.
- R4/R5는 실제 독성전문가 검토와 좁게 정의된 Context of Use가 필요합니다.
- 스캔 PDF OCR은 포함하지 않습니다.
- 실사용 confidential 자료에는 인증, 암호화, tenant isolation, 보존·삭제정책 및 접근감사가 필요합니다.
