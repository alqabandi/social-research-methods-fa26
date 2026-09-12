#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="${0:A:h}"
ROOT_DIR="${SCRIPT_DIR:h}"
MATERIALS_DIR="$ROOT_DIR/materials"
SITE_MATERIALS_DIR="$ROOT_DIR/_site/materials"

if command -v quarto >/dev/null 2>&1; then
  QUARTO="$(command -v quarto)"
else
  QUARTO="/Applications/RStudio.app/Contents/Resources/app/quarto/bin/quarto"
fi

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

if [[ ! -x "$QUARTO" ]]; then
  print -u2 "Quarto was not found."
  exit 1
fi

if [[ ! -x "$CHROME" ]]; then
  print -u2 "Google Chrome was not found."
  exit 1
fi

python3 "$SCRIPT_DIR/check-syllabus-translation.py"

cd "$ROOT_DIR"
"$QUARTO" render

render_pdf() {
  local name="$1"
  local html="$SITE_MATERIALS_DIR/$name.html"
  local pdf="$MATERIALS_DIR/$name.pdf"
  local html_uri

  if [[ ! -f "$html" ]]; then
    print -u2 "Rendered HTML was not found: $html"
    exit 1
  fi

  html_uri="$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve().as_uri())' "$html")"

  "$CHROME" \
    --headless \
    --disable-gpu \
    --no-pdf-header-footer \
    --run-all-compositor-stages-before-draw \
    --print-to-pdf="$pdf" \
    "$html_uri"

  cp "$pdf" "$SITE_MATERIALS_DIR/"
  print "Created: $pdf"
}

render_pdf "manahij-albahth-alijtimai-fall-2026"
render_pdf "manahij-albahth-alijtimai-fall-2026.en"
render_pdf "research-proposal-rubric-ar"
render_pdf "research-proposal-rubric-en"
render_pdf "presentation-oral-discussion-rubric-ar"
render_pdf "presentation-oral-discussion-rubric-en"

print "Rendered website: $ROOT_DIR/_site"
