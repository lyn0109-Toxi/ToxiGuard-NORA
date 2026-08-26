# ToxiGuard NORA GitHub 업로드 안내

## 1. GitHub에서 빈 저장소 만들기

다음 설정을 권장합니다.

- Repository name: `ToxiGuard-NORA`
- Visibility: **Private** 권장
- Initialize this repository: 선택하지 않음
  - README 추가 안 함
  - `.gitignore` 추가 안 함
  - License 추가 안 함

저장소 주소 예시:

```text
https://github.com/lyn0109-Toxi/ToxiGuard-NORA
```

## 2. 권장 방법 — GitHub Desktop

1. `ToxiGuard-NORA-v0.4.0-github-ready.zip`을 압축 해제합니다.
2. GitHub Desktop에서 **File → Add local repository**를 선택합니다.
3. 압축을 해제한 `ToxiGuard-NORA` 폴더를 선택합니다.
4. 저장소가 아직 초기화되지 않았다면 **Create a repository**를 선택합니다.
5. Commit summary에 다음을 입력합니다.

```text
feat: establish ToxiGuard NORA EarlyTox v0.4.0
```

6. **Publish repository**를 누르고 Private 설정을 확인합니다.

## 3. 터미널을 사용하는 방법

압축 해제 폴더에서 실행합니다.

```bash
cd ToxiGuard-NORA

git init -b main
git add .
git commit -m "feat: establish ToxiGuard NORA EarlyTox v0.4.0"
git remote add origin https://github.com/lyn0109-Toxi/ToxiGuard-NORA.git
git push -u origin main

git tag -a v0.4.0 -m "ToxiGuard NORA EarlyTox v0.4.0"
git push origin v0.4.0
```

## 4. Git bundle을 사용하는 방법

`ToxiGuard-NORA-v0.4.0.bundle`에는 준비된 커밋과 태그가 포함되어 있습니다.

```bash
git clone ToxiGuard-NORA-v0.4.0.bundle ToxiGuard-NORA
cd ToxiGuard-NORA
git remote set-url origin https://github.com/lyn0109-Toxi/ToxiGuard-NORA.git
git push -u origin main
git push origin v0.4.0
```

## 5. 업로드 후 확인

GitHub Actions의 **NORA Validation**이 통과하는지 확인합니다.

검증 내용:

- Python 3.11 / 3.12
- Python compile
- 14개 unit/regression test
- Repository safety guard
- Streamlit 화면 smoke test
- TG-PTO-ET ontology site validation
- OWL/RDF 및 SHACL parsing

## 6. Streamlit Community Cloud 배포

- Repository: `lyn0109-Toxi/ToxiGuard-NORA`
- Branch: `main`
- Main file path: `streamlit_app.py`
- Python: 3.11 또는 3.12

현재 v0.4.0은 별도의 API secret이 필요하지 않습니다.

## 7. GitHub Pages 온톨로지 사이트

저장소의 `site/` 폴더는 GitHub Pages용입니다. `main`에 push하면 `.github/workflows/pages.yml`이 사이트를 배포합니다.

GitHub 저장소에서 다음을 확인합니다.

```text
Settings → Pages → Source: GitHub Actions
```

## 8. 업로드하면 안 되는 파일

다음 파일·폴더는 `.gitignore`에 포함되어 있으며 GitHub에 올리지 않습니다.

```text
.env
.streamlit/secrets.toml
.nora_data/
*.db
*.sqlite
validation_reports/*.md
dist/
.venv/
__pycache__/
실제 sponsor confidential 문서
```
