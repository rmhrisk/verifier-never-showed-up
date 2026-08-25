# Whitepaper build

`index.html` is the source of truth. This directory rebuilds the Word version from it.

    python3 extract.py      # pull structure, record, diagnostic, sources out of ../../index.html
    node build.js           # emit ../../verifier-never-showed-up.docx

`figs/` holds figures rasterised from the page's inline SVGs at 2x, plus the six
bundled photographs. Regenerate them with `extract.py --figs`, which needs Playwright.

The document drops what does not survive paper: the record filters, the scorecard
scoring, and the quiz. The record becomes Appendix A as a real table, the diagnostic
becomes Appendix B as a numbered list.
