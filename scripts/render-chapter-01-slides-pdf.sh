#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="${0:A:h}"
ROOT_DIR="${SCRIPT_DIR:h}"
SLIDE_NAME="chapter_01_slide_deck"
SLIDE_QMD="$ROOT_DIR/slides/$SLIDE_NAME.qmd"
SLIDE_HTML="$ROOT_DIR/_site/slides/$SLIDE_NAME.html"
SLIDE_PDF="$ROOT_DIR/slides/$SLIDE_NAME.pdf"
SITE_PDF="$ROOT_DIR/_site/slides/$SLIDE_NAME.pdf"

if command -v quarto >/dev/null 2>&1; then
  QUARTO="$(command -v quarto)"
else
  QUARTO="/Applications/RStudio.app/Contents/Resources/app/quarto/bin/quarto"
fi

if [[ -x "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]]; then
  CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
elif command -v google-chrome >/dev/null 2>&1; then
  CHROME="$(command -v google-chrome)"
else
  print -u2 "Google Chrome was not found."
  exit 1
fi

if [[ ! -x "$QUARTO" ]]; then
  print -u2 "Quarto was not found."
  exit 1
fi

cd "$ROOT_DIR"
"$QUARTO" render "$SLIDE_QMD" --to revealjs

if [[ ! -f "$SLIDE_HTML" ]]; then
  print -u2 "Rendered slide HTML was not found: $SLIDE_HTML"
  exit 1
fi

HTML_URI="$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve().as_uri())' "$SLIDE_HTML")"

"$CHROME" \
  --headless \
  --disable-gpu \
  --no-pdf-header-footer \
  --run-all-compositor-stages-before-draw \
  --virtual-time-budget=5000 \
  --print-to-pdf="$SLIDE_PDF" \
  "${HTML_URI}?print-pdf"

mkdir -p "${SITE_PDF:h}"
cp "$SLIDE_PDF" "$SITE_PDF"

print "Created: $SLIDE_HTML"
print "Created: $SLIDE_PDF"
