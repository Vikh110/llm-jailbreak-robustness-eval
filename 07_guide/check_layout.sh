#!/usr/bin/env bash
# Compiles the guide through LaTeX with a log, and lists anything that overflows the page.
cd "$(dirname "$0")"
mkdir -p _diag
pandoc chapters/*.md -o _diag/guide.tex --standalone --from markdown+smart \
  --toc --toc-depth=2 --number-sections --top-level-division=chapter \
  -V documentclass=report -V papersize=a4 -V geometry:margin=2.4cm \
  -V mainfont="Cambria" -V sansfont="Calibri" -V monofont="Consolas" -V mathfont="Cambria Math" -V mainfontoptions=Ligatures=NoCommon -V sansfontoptions=Ligatures=NoCommon \
  -V fontsize=11pt -V colorlinks=true -V linkcolor=gnavy -V urlcolor=gblue -V toccolor=gnavy \
  --lua-filter=boxes.lua -H header.tex --syntax-highlighting=tango
xelatex -interaction=nonstopmode -output-directory=_diag _diag/guide.tex > _diag/run.txt 2>&1
echo "xelatex exit: $?"
grep -E "Overfull|Missing character|Undefined control|^!" _diag/guide.log | sort | uniq -c | sort -rn | head -30
echo "--- end of layout check"
