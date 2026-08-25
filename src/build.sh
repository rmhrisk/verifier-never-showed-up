#!/bin/bash
# Assemble index.html from the source fragments, then run both checks.
set -e
cd "$(dirname "$0")"
python3 gen_diagnostic.py            # regenerate the static diagnostic markup
python3 gen_category_chart.py        # regenerate the category chart from RECORD
cat part1_head.html part2_open.html part3a.html part3b.html \
    part4.html part5.html part6_close.html part7_js.html > ../index.html
python3 verify_build.py              # content, structure, citations, rendered-vs-source
python3 audit.py                     # figure overflow, collisions, connector routing
echo "build ok"
