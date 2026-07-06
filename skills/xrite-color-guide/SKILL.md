---
name: xrite-color-guide
description: Color science reference for graphic arts.
version: 0.1.0
author: Hermes
metadata:
  hermes:
    tags: [Color, Graphic Arts, Color Management, CIE, Densitometry]
---

# X-Rite Color Guide Reference

References the X-Rite Color Guide (L11-029) for color communication, measurement, CIE color systems, instrumentation, color management, and glossary terms in digital imaging and graphic arts. Does not replace a spectrophotometer manual or profile-building tool. Self-contained reference: all source text and supplementary material are stored locally within the skill.

## For Researchers

For deeper treatment with equations, formal definitions, open research questions, and bibliography, see the supplementary files:

- `references/release-notes.md` — Research digest: formal equations for CIE LAB, CIEDE2000, spectrophotometry, the metamerism constraint, device calibration math, gamut compression, glossary of formal terms, and 5 open research questions.
- `references/bibliography.md` — Primary sources from the original document and key standards bodies (CIE, ICC, ANSI IT8).

## When to Use

- "Explain CIE L\*a\*b\* or CIE XYZ"
- "What is metamerism?"
- "How does a spectrophotometer differ from a densitometer?"
- "Describe the color management workflow (calibration vs. characterization)"
- "What are the standard CIE illuminants (D50, D65)?"
- "How is ink formulation done from spectral data?"
- "Define a glossary term: [term]"
- "What is delta E / color tolerancing?"
- "Explain additive vs. subtractive primaries"

## Prerequisites

None. The full extracted text is stored as a reference file within this skill: `references/xrite-color-guide-text.md`.

## How to Run

1. Read the reference file `references/xrite-color-guide-text.md` via `read_file` to locate the relevant section.
2. Present the excerpt with source attribution.

## Quick Reference

| Section | Key Topics |
|---------|-----------|
| Color Communication | Light → Object → Viewer triad, color workflow challenges |
| Understanding Color | Visible spectrum (400–700nm), spectral data, RGB additive primaries, CMY/CMYK subtractive primaries, HSL dimensions |
| CIE Color Systems | CIE XYZ, Standard Observer (2°/10°), xy chromaticity diagram, CIE L\*a\*b\*, CIE L\*C\*h°, standard illuminants (A, B, C, D50, D65, F series) |
| Spectral vs. Tristimulus | Device/illuminant dependence vs. independence, metamerism detection |
| Instrumentation | Densitometer (density/strength), colorimeter (tristimulus RGB → L\*a\*b\*), spectrophotometer (spectral fingerprint, 31 points at 10nm) |
| Color Management | Device calibration, device characterization/profiling (IT8 targets), ICC profiles, ColorSync/ICM, gamut compression |
| Ink Formulation | Spot color matching from spectral data, X-RiteColor Master |
| Color Control | Color bars, densitometric process control, control limits, ATS system |
| Color Verification | Tolerancing: CIELAB (∆E sphere), CMC/CIE94/CIE2000 (elliptical), typical tolerance 2–6 ∆E |
| Glossary | ~80 defined terms from Absorbance to Yellow |

## Procedure

1. **Read the reference file** — Use `read_file` on `references/xrite-color-guide-text.md` to locate the relevant section. The file is ~92k chars; use `offset`/`limit` to page through it.

2. **Locate the relevant section** — Use `search_files` or `read_file` on `references/xrite-color-guide-text.md` to find the section matching the user's question. Key section headings from the TOC:
   - "Color Communication" (line ~29)
   - "UNDERSTANDING COLOR" (line ~98)
   - "THE CIE COLOR SYSTEMS" (line ~200)
   - "SPECTRAL DATA VS. TRISTIMULUS DATA" (line ~250)
   - "Color Measurement and Control" / "INSTRUMENTATION" (line ~300)
   - "COLOR MANAGEMENT" (line ~350)
   - "INK FORMULATION" (line ~400)
   - "COLOR CONTROL" (line ~410)
   - "COLOR VERIFICATION" (line ~430)
   - "Glossary" (line ~500+)

3. **Present the answer** — Read the relevant lines and summarize or quote the passage with attribution to the X-Rite Color Guide.

## Pitfalls

- PDF extraction mangles tables, figures, and diagrams — CIE chromaticity diagrams, spectral curves, and color space illustrations are missing from the text output.
- The document is from 2004; some technology references (ColorShop X, MonacoOPTIX, specific X-Rite models) are dated, though the color science fundamentals remain current.
- Glossary terms are embedded in prose, not a structured data format — use `search_files` to find specific terms.
- The reference file `references/xrite-color-guide-text.md` is ~92k chars; use `offset`/`limit` with `read_file` to page through it rather than reading the entire file.

## Verification

Confirm the Glossary section in `references/xrite-color-guide-text.md` contains the term "Metamerism" with its definition by using `read_file` and `search_files`. The definition should match: "The phenomenon where two colors appear to match under one light source, yet do not match under a different light source."

Example:
```
search_files(pattern="Metamerism", path="references/xrite-color-guide-text.md")
```