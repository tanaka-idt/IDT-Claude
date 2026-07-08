#!/bin/bash
# Render the 7 BOSS Revolution crypto-flow screen designs to PNG (2x scale)
# via headless Chrome. Output: crypto_screen_N.png in the repo root.
set -e
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
DIR="$(cd "$(dirname "$0")" && pwd)"
OUT="$(dirname "$DIR")"
for i in 1 2 3 4 5 6 7; do
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars \
    --window-size=390,844 --force-device-scale-factor=2 \
    --virtual-time-budget=12000 \
    --screenshot="$OUT/crypto_screen_$i.png" \
    "file://$DIR/s$i.html" 2>/dev/null
  echo "rendered crypto_screen_$i.png"
done
