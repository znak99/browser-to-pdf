# browser-to-pdf

FastAPI와 Playwright를 사용해 URL을 입력하면 해당 페이지를 PDF로 내려받을 수 있는 SSR 사이트입니다. Python과 FastAPI는 Docker 컨테이너 안에서 실행하는 것을 기준으로 구성했습니다.

## 기능

- 서버 사이드 렌더링 기반 단일 페이지 UI
- `http` 또는 `https` URL 입력 후 즉시 PDF 다운로드
- JavaScript 기반 페이지를 위한 Chromium 렌더링
- Docker 컨테이너에서 바로 실행 가능한 구성
- 컨테이너 상태 확인용 `/health` 엔드포인트 제공

## Docker 실행

```bash
docker compose up --build
```

또는 단일 이미지로 직접 실행할 수 있습니다.

```bash
docker build -t browser-to-pdf .
docker run --rm -p 8100:8100 browser-to-pdf
```

브라우저에서는 `http://127.0.0.1:8100`으로 접속합니다.

## 구조

```text
app/
  main.py
  services/
    pdf.py
  static/
    styles.css
  templates/
    base.html
    index.html
```

## 동작 개요

1. 사용자가 SSR 폼에 대상 URL을 입력합니다.
2. 서버가 URL을 정규화하고 허용 스킴을 검증합니다.
3. Playwright Chromium이 페이지를 열고 네트워크 안정화를 기다립니다.
4. A4 PDF를 생성해 첨부 파일로 응답합니다.
