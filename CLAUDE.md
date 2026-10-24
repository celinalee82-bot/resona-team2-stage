# RESONA 무대 3D 시뮬레이터 — Claude용 실행 메모

이 폴더를 연 Claude에게: 사용자가 「열어줘 / 실행해줘」라고 하면 아래대로.

## 열기
1. **보기만**: `open -a "Google Chrome" RESONA_무대3D_더블클릭.html` (윈도우: 크롬·엣지로 이 파일 열기)
   - 3D 엔진·폰트가 파일 안에 들어 있어서 서버·인터넷 불필요
2. **레조나와 실시간 연결까지**: 이 폴더에서 `bash 시작.command`
   - 중계(`relay.py`, ws://localhost:9980) + 화면 서버(8977)를 켜고 크롬으로 `stage_3d.html`을 엶 (맥 전용, python3 필요)
   - 끄기: 그 터미널 탭에서 Ctrl+C 또는 창 닫기
   - 이미 9980·8977 포트가 쓰이고 있으면 그건 건너뜀

## 고칠 때
- 원본은 `stage_3d.html` 하나. 고친 뒤 **반드시** `python3 tools/build_standalone.py`로 `RESONA_무대3D_더블클릭.html`을 다시 만들 것 (안 하면 두 버전이 달라짐)
- 확인은 `bash 시작.command`로 연 http://localhost:8977/stage_3d.html 에서
- `RESONA_무대3D_더블클릭.html`을 손으로 고치지 말 것 (다음 빌드 때 덮어써짐)

## 하지 말 것
- `stage_3d.html`을 file://로 직접 열지 말 것 — `lib/`의 모듈을 크롬이 막음. 서버(시작.command)로 열거나 한 파일 버전을 쓸 것
- `lib/` 폴더를 지우거나 옮기지 말 것

## 파일
- `stage_3d.html` — 원본(3D 콘서트 무대). 고치면 한 파일 버전을 다시 만들어야 함
- `RESONA_무대3D_더블클릭.html` — 한 파일 버전(원본 + three.js 0.160 + 네온 폰트 내장)
- `relay.py` — resona.html → 시뮬레이터 중계
- `README.md` — 기능·조작·사이즈 전체 설명
