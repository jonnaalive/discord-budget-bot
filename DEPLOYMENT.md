# Railway 상시 실행

Discord 봇은 Gateway에 계속 연결되어야 하므로 Railway 장기 실행 서비스로 배포한다.

필수 환경변수:

- `DISCORD_BOT_TOKEN`
- `GOOGLE_SHEET_ID`, `GOOGLE_SHEET_NAME`
- `FAMILY_SHEET_ID`, `FAMILY_SHEET_NAME`, `FAMILY_CHANNEL_NAME`
- `OPENAI_API_KEY`
- `GOOGLE_CREDENTIALS_JSON`: `credentials.json` 전체 내용을 한 줄 JSON으로 등록

빌드와 실행 설정은 `Dockerfile` 및 `railway.toml`에 정의되어 있다. 실패 시 최대
10회 자동 재시작한다.
