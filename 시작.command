#!/bin/bash
# RESONA 무대 3D — 더블클릭으로 켜기
# 1) 레조나 중계(relay.py, 9980) 2) 화면 서버(8977) 를 켜고 크롬으로 연다.
# 끄기: 이 터미널 창을 닫으면 둘 다 꺼진다.

cd "$(dirname "$0")"
PORT=8977
ROOT="$(cd ../.. && pwd)"            # KAIST CT 2 — 04_참고자료 영상도 ?video= 로 열 수 있게

PIDS=()
if ! lsof -nP -iTCP:9980 -sTCP:LISTEN >/dev/null 2>&1; then
  python3 relay.py & PIDS+=($!)
fi
if ! lsof -nP -iTCP:$PORT -sTCP:LISTEN >/dev/null 2>&1; then
  python3 -m http.server $PORT --directory "$ROOT" >/dev/null 2>&1 & PIDS+=($!)
fi
trap 'kill ${PIDS[@]} 2>/dev/null' EXIT

sleep 1
URL="http://localhost:$PORT/05_resona_console/stage_sim/stage_3d.html"
open -a "Google Chrome" "$URL" 2>/dev/null || open "$URL"

echo ""
echo "RESONA 무대 3D 열림 → $URL"
echo "레조나(resona.html)에서 「WS 연결」을 누르면 LIVE 로 바뀝니다."
echo "끄려면 이 창을 닫으세요."
wait
