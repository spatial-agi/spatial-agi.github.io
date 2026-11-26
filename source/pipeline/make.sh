#!/bin/bash
# Content rebuild from the read-only book source and the supplied final PDF.
set -euo pipefail
P="$(cd "$(dirname "$0")" && pwd)"
cd "$P"
PY="${PYTHON:-python3}"
BOOK="$($PY -c 'from book_source import BOOK; print(BOOK)')"
PDF="$($PY -c 'from book_source import PDF; print(PDF)')"
mkdir -p build/html data
if [[ "${1:-}" != "--skip-latex" ]]; then
  "$PY" stage.py
  (cd stage && "${LATEXML:-latexml}" --path="$BOOK" --destination=../build/book.xml book_web.tex > ../build/latexml.log 2>&1)
  "${LATEXMLPOST:-latexmlpost}" --format=html5 --nographicimages --pmml --mathtex --nodefaultresources --destination=build/html/book.html build/book.xml > build/latexmlpost.log 2>&1
fi
"$PY" pdf_metadata.py
"$PY" extract_refs.py
"$PY" prepare_content_figures.py
if [[ ! -f build/handbook-web.pdf || "$PDF" -nt build/handbook-web.pdf ]]; then
  gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.6 -dPDFSETTINGS=/ebook -dColorImageResolution=200 -dGrayImageResolution=200 -dDownsampleColorImages=true -dNOPAUSE -dQUIET -dBATCH -sOutputFile=build/handbook-web.pdf "$PDF"
fi
"$PY" build_site.py
OUTPUT="$($PY -c 'from book_source import DIST; print(DIST)')"
if [[ -n "${PAGEFIND:-}" ]]; then
  "$PAGEFIND" --site "$OUTPUT" --output-subdir pagefind > build/pagefind.log 2>&1
else
  npx --yes pagefind@1.3.0 --site "$OUTPUT" --output-subdir pagefind > build/pagefind.log 2>&1
fi
printf 'Content build ready: %s\n' "$OUTPUT"
printf 'To update the local website after verification: %s publish_content.py\n' "$PY"
