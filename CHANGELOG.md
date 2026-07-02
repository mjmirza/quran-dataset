# Changelog

All notable changes to this dataset are recorded here. The format follows Keep a Changelog, and the project uses semantic versioning.

## [1.1.0] - 2026-07-02

### Added

- Word by word breakdown on every ayah. each word carries its index, text, a deterministic Buckwalter transliteration, and its letter and character counts.
- Ayah level Buckwalter transliteration column in the flat JSONL and CSV.
- Two new validation checks. the word breakdown length equals the word count on every ayah, and the word breakdown rejoins to the exact ayah text.

### Note

- Per word meaning, root, lemma, and grammar are intentionally excluded. those sources are GPL or copyrighted and cannot be relicensed under CC BY 4.0.

## [1.0.0] - 2026-07-02

### Added

- First release of the Quran Core Dataset, all 114 surahs and 6236 ayahs in the Uthmani script.
- Normalized nested structure, corpus then surahs then ayahs, in `data/quran.json`.
- Flat `data/quran.jsonl` and `data/quran.csv` for notebook and spreadsheet workflows.
- Per ayah metadata, the juz, hizb, hizb quarter, manzil, ruku, mushaf page, and sajda marker.
- Computed word and letter counts at the ayah, surah, and corpus level.
- Revelation type and revelation order per surah.
- Content hashes on every ayah, every surah, and the corpus.
- Deterministic builder in `src/build.py`.
- Independent validator in `src/validate.py` with six layers.
- Validation report in `docs/VALIDATION.md`, verdict PASS across all six layers, letter level agreement 99.903 percent against an independent dataset, zero mismatches against the source.
