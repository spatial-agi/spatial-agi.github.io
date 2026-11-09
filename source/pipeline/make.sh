#!/bin/zsh
# Full pipeline: stage -> LaTeXML -> verify -> latexmlpost -> figures -> refs. Usage: ./make.sh [--skip-latex]
set -e
P=${0:A:h}; B=$P/../../Spt-Intell-share-paper; PY=~/miniforge3/envs/bookweb/bin/python
cd $P
if [[ "$1" != "--skip-latex" ]]; then
  ~/miniforge3/envs/figgen/bin/python tikz_figs.py
  $PY stage.py
  (cd stage && latexml --path=$B --destination=../build/book.xml book_web.tex > ../build_latexml.log 2>&1)
  tail -1 build_latexml.log
  latexmlpost --format=html5 --nographicimages --pmml --mathtex --nodefaultresources --destination=build/html/book.html build/book.xml > build/latexmlpost.log 2>&1
fi
$PY extract_refs.py
$PY verify_numbers.py | head -3
cat $(find stage -name "*.tex" ! -path stage/main.tex ! -path stage/command.tex) | grep -v "^\s*%" | grep -oE "\\\\includegraphics(\[[^]]*\])?\{[^}]+\}" | sed -E 's/.*\{([^}]+)\}/\1/' | sort -u > data/graphics.txt
$PY figures.py
# web PDF (images downsampled to 200 dpi)
if [[ "$1" != "--skip-latex" || ! -f build/handbook-web.pdf ]]; then
  gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.6 -dPDFSETTINGS=/ebook -dColorImageResolution=200 -dGrayImageResolution=200 -dDownsampleColorImages=true -dNOPAUSE -dQUIET -dBATCH -sOutputFile=build/handbook-web.pdf $B/main.pdf
fi
$PY build_site.py
(cd .. && npx --yes pagefind@1.3.0 --site dist --output-subdir pagefind > pipeline/build/pagefind.log 2>&1 && tail -3 pipeline/build/pagefind.log)
