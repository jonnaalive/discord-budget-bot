# Discord 가계부 봇

디스코드 메시지로 `품목, 금액`을 입력하면 AI가 자동 분류하고 구글 시트에 기록하는 봇.

## 기능
- **자동 분류**: OpenAI가 품목을 9개 카테고리(비필수 식비, 필수 식비, 필수 소비 등)로 분류
- **필수 여부 판단**: 카테고리에 따라 필수/비필수 자동 판단
- **구글 시트 기록**: 날짜, 금액, 품목명, 대분류, 필수여부를 자동 기록

## 설정

### 1. 디스코드 봇 생성
1. [Discord Developer Portal](https://discord.com/developers/applications) 접속
2. **New Application** → 이름 입력 → 생성
3. **Bot** 탭 → **Add Bot**
4. **TOKEN** 복사 (`.env`에 사용)
5. **Privileged Gateway Intents**에서 **Message Content Intent** 활성화
6. **OAuth2 → URL Generator** → `bot` 체크 → 권한: `Send Messages`, `Read Message History`
7. 생성된 URL로 서버에 봇 초대

### 2. 구글 서비스 계정
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 프로젝트 생성 → Google Sheets API 활성화
3. 서비스 계정 생성 → JSON 키 다운로드
4. `credentials.json`으로 이름 변경 후 프로젝트 루트에 배치
5. 구글 시트에 서비스 계정 이메일을 편집자로 공유

### 3. 환경 변수
```bash
cp .env.example .env
```
`.env` 파일에 실제 값 입력:
```
DISCORD_BOT_TOKEN=실제_디스코드_봇_토큰
GOOGLE_SHEET_ID=구글_시트_ID
GOOGLE_SHEET_NAME=시트_탭_이름
OPENAI_API_KEY=OpenAI_API_키
```

### 4. 설치 & 실행
```bash
pip install -r requirements.txt
python bot.py
```

## 사용법

| 입력 | 설명 |
|------|------|
| `치킨, 25000원` | 가계부 기록 |
| `스타벅스, 6500` | 원 없이도 가능 |
| `!start` | 시작 안내 메시지 |
| `!help` | 도움말 |

## 구글 시트 구조

| A열 | B열 | C열 | D열 | E열 |
|-----|-----|-----|-----|-----|
| 날짜 | 금액 | 품목명 | 대분류 | 필수여부 |
