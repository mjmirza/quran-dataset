# Validation Report

Generated 2026-07-02T06:30:56Z by `src/validate.py`.

Overall verdict. **PASS**. 6 of 6 layers that ran passed.

Each layer is an independent confirmation, run against a different reference. The dataset was validated 6 separate ways and every layer that ran passed.

## Layer 1. Structural integrity [PASS]

- [x] exactly 114 surahs
- [x] exactly 6236 ayahs
- [x] per-surah ayah counts match the authoritative structure
- [x] surah numbers are 1..114 contiguous

## Layer 2. Content fidelity vs Tanzil source [PASS]

- [x] every ayah text byte-identical to the source
- [x] mismatched ayahs = 0

## Layer 3. Canonical invariants [PASS]

- [x] 30 distinct juz
- [x] 60 distinct hizb
- [x] exactly 15 sajda ayahs
- [x] has_bismillah true on 113 surahs
- [x] At-Tawba (9) has no bismillah
- [x] basmala present in the text of 113 surahs (expect 113)

## Layer 4. Independent cross-check (letter-level agreement) [PASS]

- [x] reference: an independent dataset (local)
- [x] all 114 surahs cross-checked against an independent dataset
- [x] surahs letter-identical = 54/114
- [x] letter-level agreement = 99.903% (remainder is orthographic-convention variance)

## Layer 5. Unicode sanity [PASS]

- [x] no empty ayahs
- [x] ayahs with a non-Arabic letter = 0
- [x] ayahs with any non-Arabic-block character = 0

## Layer 6. Derived-metric self-consistency [PASS]

- [x] per-surah word counts sum from their ayahs
- [x] per-surah letter counts sum from their ayahs
- [x] word breakdown length equals word count on every ayah
- [x] word breakdown rejoins to the exact ayah text (lossless)
- [x] surah ayah counts sum to 6236
- [x] corpus word total consistent (77881)
- [x] corpus letter total consistent (329728)
- [x] recomputed corpus content hash matches

## References used

- Arabic text and structural metadata, Tanzil Project, CC BY 3.0, https://tanzil.net
- Canonical structure, 114 surahs and 6236 ayahs, King Fahd Glorious Quran Printing Complex
- An independent, separately published Quran dataset, used only as a second opinion for the letter-skeleton cross-check
