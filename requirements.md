# 의존성 (Dependencies)

## 실행 환경

| 항목 | 요구사항 |
|---|---|
| Python | 3.10 이상 |
| Claude CLI | 최신 버전 (`claude` 명령 PATH 등록 필요) |
| OS | macOS / Linux / Windows (WSL) |

## Python 패키지

```
streamlit>=1.40.0
fastmcp>=0.3.0
```

## 설치 방법

```bash
pip3 install -r requirements.txt
```

## Claude CLI 설치

에이전트 채팅 기능을 사용하려면 Claude CLI가 설치되어 있어야 합니다.

```bash
# npm을 통해 설치
npm install -g @anthropic-ai/claude-code

# 설치 확인
claude --version
```

> Claude CLI 미설치 시, 위키 탐색·검색 기능은 정상 동작하며 에이전트 채팅 패널만 오류 메시지를 표시합니다.

## 추가 의존성 (선택)

PDF → 위키 변환 파이프라인을 사용할 경우:

```bash
# macOS
brew install poppler   # pdftotext 포함

# Ubuntu/Debian
apt-get install poppler-utils
```
