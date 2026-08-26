# NORA GitHub 운영방식

## 1. 저장소 목적

`ToxiGuard-NORA`는 NORA 제품의 단일 기준 저장소입니다. 앱 코드, TG-PTO-ET, SHACL, 결정규칙, Golden Case, 검증보고서와 운영문서를 같은 버전으로 관리합니다.

## 2. 브랜치

| 브랜치 | 역할 |
|---|---|
| `main` | CI와 과학적 검증을 통과한 배포 가능 상태 |
| `feature/*` | UI, 문서 작업공간, 보고서 등 기능 |
| `science/*` | 독성 개념·방법론·검증 프레임 변경 |
| `ontology/*` | TG-PTO-ET와 SHACL 변경 |
| `rule/*` | 결정규칙, Gate, Score, Evidence Role 변경 |
| `fix/*` | 버그 수정 |
| `docs/*` | 문서 전용 변경 |

1인 개발 단계에서는 별도의 `develop` 브랜치를 두지 않습니다. 짧은 작업 브랜치를 `main`에서 만들고 Pull Request를 통해 병합합니다.

## 3. Issue → Branch → PR

```text
Issue에서 문제와 의사결정 정의
→ main에서 전용 Branch 생성
→ 코드·온톨로지·규칙·테스트 변경
→ Pull Request
→ Python 3.11/3.12 CI
→ 과학적 검토
→ main 병합
→ Release tag
```

## 4. 과학적 변경 PR 필수항목

- Question of Interest와 Context of Use
- Product modality와 endpoint
- Rule ID 또는 ontology entity
- 변경 전·후 Evidence Role
- 영향을 받는 Golden Case
- Missing/negative/out-of-domain 경계 테스트
- Residual uncertainty와 false-negative 영향
- 전문가 검토자와 승인상태

## 5. main 보호 권장 설정

1. Pull Request 없이 main 변경 금지
2. `Python 3.11`과 `Python 3.12` status check 필수
3. review conversation 해결 전 병합 금지
4. force push와 branch deletion 금지
5. 외부 공동개발자가 생기면 승인 1명 필수

## 6. 릴리스

```bash
python scripts/validate.py
git tag -a v0.4.0 -m "ToxiGuard NORA EarlyTox v0.4.0"
git push origin main --tags
```

태그가 push되면 GitHub Actions가 검증 후 versioned ZIP과 GitHub Release를 생성합니다.
