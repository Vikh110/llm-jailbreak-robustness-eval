#!/usr/bin/env bash
# Builds the project guide PDF from the Markdown chapters (pandoc + xelatex).
# Usage: bash build_guide.sh [output.pdf] [chapter files...]
set -e
cd "$(dirname "$0")"
OUT="${1:-Project_Guide.pdf}"
shift || true
FILES=("$@")
if [ ${#FILES[@]} -eq 0 ]; then FILES=(chapters/*.md); fi
pandoc "${FILES[@]}" -o "$OUT" \
  --pdf-engine=xelatex --from markdown+smart \
  --toc --toc-depth=2 --number-sections --top-level-division=chapter \
  -V documentclass=report -V papersize=a4 -V geometry:margin=2.4cm \
  -V mainfont="Cambria" -V sansfont="Calibri" -V monofont="Consolas" -V mathfont="Cambria Math" -V mainfontoptions=Ligatures=NoCommon -V sansfontoptions=Ligatures=NoCommon \
  -V fontsize=11pt -V colorlinks=true -V linkcolor=gnavy -V urlcolor=gblue -V toccolor=gnavy \
  --lua-filter=boxes.lua -H header.tex --syntax-highlighting=tango
echo "built $OUT"
