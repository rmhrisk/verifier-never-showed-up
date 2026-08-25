# The Verifier Never Showed Up

Thirty years of digital identity programmes, sorted by how they actually failed, and
why the half of the system that decides adoption is the half nobody funds.

**Read it: https://rmhrisk.github.io/verifier-never-showed-up/**

First written September 2025 and presented at the State-Endorsed Digital Identity
Summit at Utah Valley University that October. Substantially revised and published
here in August 2026.

## What is in it

A record of 32 identity programmes from 1997 to the present, each tagged with the
failure modes that actually applied to it rather than a single cause, filterable by
kind and by mode. Eleven failure modes in four families, five of them structural.
A seventeen-question diagnostic you can run against a real proposal. Nineteen
diagrams and a set of public-domain artifacts spanning about four thousand years.

The argument, in five claims:

1. Acceptance decides, and it is nobody's job.
2. The mathematics was never the problem. In this sample, none of the identified failures was cryptographic.
3. Residual responsibility sets the value ceiling.
4. Launch is the start of the bill.
5. Change what gets counted, or nothing else changes.

## Building

`index.html` is a single self-contained file with every image inlined. It is
assembled from the fragments in `src/`:

```sh
./src/build.sh
```

That regenerates the diagnostic markup and the category chart from their single
sources of truth (the chart is computed from the `RECORD` array), concatenates
the fragments, and runs two checks:

- `verify_build.py` — content, structure, citations, pointer labels, and a
  comparison of the rendered DOM against the source markup
- `audit.py` — SVG text overflow, text collisions, and connectors crossing boxes

Both must pass before publishing.

## Status

The sources list carries 24 entries, 23 with resolved links. The claims that are not
verified against a primary source are named in the "What this post does not establish"
section, .

## Credits

Image sources and licences are in [CREDITS.md](CREDITS.md). All are public domain,
CC0 or OGL, bundled locally rather than hotlinked.
