# Quran Core Dataset

A clean, uniquely structured, independently validated dataset of the Arabic Quran, free for anyone to use under CC BY 4.0.

![License](https://img.shields.io/badge/license-CC%20BY%204.0-brightgreen)
![Surahs](https://img.shields.io/badge/surahs-114-blue)
![Ayahs](https://img.shields.io/badge/ayahs-6236-blue)
![Validation](https://img.shields.io/badge/validation-6%2F6%20layers%20pass-success)
![Script](https://img.shields.io/badge/script-Uthmani-lightgrey)

## Why this exists

Most Quran datasets make you take the text on faith. You cannot tell where the numbers came from, whether the verses are complete, or whether anything drifted from the source. This one hands you the proof with the data. Every verse is checked, every count is computed in front of you, and every file can be rebuilt from source in one command.

The Arabic text of the Quran is public domain. The value here is the structure and the proof around it. Drop it into an app, a search index, a machine learning pipeline, or a study tool and trust that every verse is where it should be and reads exactly as the source.

## What you get

- Every one of the 6236 ayahs across all 114 surahs, in the Uthmani script.
- A normalized shape, corpus then surahs then ayahs, so surah metadata is never repeated on every row.
- Rich metadata per ayah, the juz, the hizb, the hizb quarter, the manzil, the ruku, the mushaf page, and the sajda marker where one applies.
- A word by word breakdown for every ayah, each word with its index, its text, a Buckwalter transliteration, and its letter and character counts.
- Word and letter counts computed for every ayah, every surah, and the whole corpus.
- Revelation type and revelation order for every surah.
- A content hash on every ayah, every surah, and the corpus, so you can detect any change instantly.
- Three prebuilt shapes, a nested JSON, a flat JSONL, and a CSV, so it fits an app or a notebook without conversion.
- A validation report that shows the data passed six independent checks.

## Validation, six independent ways

The dataset was checked six separate ways, and every layer that ran passed. Each layer uses a different reference, so passing all of them is six confirmations, not one repeated.

- Layer 1, structural integrity. Exactly 114 surahs and 6236 ayahs, and every per surah ayah count matches the authoritative structure.
- Layer 2, content fidelity. Every ayah is byte identical to the original source text. Zero mismatches.
- Layer 3, canonical invariants. 30 juz, 60 hizb, 15 sajda ayahs, and the basmala present on 113 surahs, absent only on At Tawba.
- Layer 4, independent cross check. The bare consonantal letters of every surah were compared against a second, separately published Quran dataset. Letter level agreement is 99.903 percent, and 54 of 114 surahs are letter identical. The small remainder is orthographic convention variance between two independent editions, which is expected and is not a fidelity defect.
- Layer 5, unicode sanity. No empty ayahs, and every character lives in an Arabic Unicode block.
- Layer 6, derived metric self consistency. Per surah counts sum to the corpus totals, the ayah counts sum to 6236, and the recomputed corpus hash matches.

The full machine generated report is in [docs/VALIDATION.md](docs/VALIDATION.md). Rebuild it yourself any time with the commands below.

## At a glance

| Measure | Value |
|---|---|
| Surahs | 114 |
| Ayahs | 6236 |
| Juz | 30 |
| Hizb | 60 |
| Hizb quarters | 240 |
| Manzils | 7 |
| Rukus | 556 |
| Mushaf pages | 604 |
| Sajda ayahs | 15 |
| Words (this edition) | 77881 |
| Letters (this edition) | 329728 |

## The shape

The primary file is `data/quran.json`. It is one object, a `dataset` header with counts, sources, and a corpus hash, then a `surahs` array. Each surah carries its names, revelation data, counts, and an `ayahs` array.

```
{
  "dataset": { "name": "...", "version": "1.0.0", "license": "CC BY 4.0", "counts": { ... }, "sources": [ ... ], "content_hash": "sha256:..." },
  "surahs": [
    {
      "number": 1,
      "name_arabic": "...",
      "name_transliteration": "Al-Faatiha",
      "name_english": "The Opening",
      "revelation": { "type": "Meccan", "order": 5 },
      "counts": { "ayahs": 7, "rukus": 1, "words": 29, "letters": 139 },
      "juz_span": [1, 1],
      "has_bismillah": true,
      "content_hash": "sha256:...",
      "ayahs": [
        {
          "number": 1,
          "verse_key": "1:1",
          "global_number": 1,
          "text": "...",
          "words": [
            { "index": 1, "text": "...", "buckwalter": "...", "letters": 5, "chars": 9 }
          ],
          "counts": { "words": 4, "letters": 19 },
          "juz": 1, "hizb": 1, "hizb_quarter": 1, "manzil": 1, "ruku": 1, "page": 1,
          "sajda": null,
          "content_hash": "sha256:..."
        }
      ]
    }
  ]
}
```

For flat workflows, `data/quran.jsonl` has one ayah per line, and `data/quran.csv` has the same rows as a spreadsheet.

## Word by word

Every ayah carries a `words` array. Each entry is one Arabic word with its position, its text, a Buckwalter transliteration, and its letter and character counts. The breakdown is a lossless split of the ayah, so rejoining the words reproduces the verse exactly, and the validator checks this on all 6236 ayahs.

Buckwalter is the standard lossless ASCII scheme used across Quran language work. It is generated here from the Arabic by a fixed, documented table, so it is deterministic and original to this dataset. It is a phonetic orthographic transliteration, not a meaning.

What the word layer deliberately does not include is per word meaning, root, lemma, or grammar. Those datasets are published under GNU GPL or under their own copyright, so they cannot be relicensed under CC BY 4.0 and are not bundled here. If you need them, fetch them from their own source and join on the verse key and the word index. Keeping them out is what lets this dataset stay cleanly free for everyone.


## A note on counts and the basmala

The word and letter counts are computed directly from the text of this edition, so they are exact for what ships here. A letter is any Unicode letter, with the tatweel and the nonspacing tashkeel marks removed. This edition merges the opening basmala into the first ayah of every surah except At Tawba, and Al Fatiha keeps the basmala as its own first ayah, so the counts include the basmala where the edition places it. The `has_bismillah` flag records this per surah, and the validator confirms it against the actual text.

## Rebuild and re validate

Nothing here is a black box. You can regenerate everything from the two source files in `data/sources` and check it yourself.

Build the dataset.

```
python3 src/build.py
```

Validate it, with the optional independent cross check.

```
python3 src/validate.py
python3 src/validate.py --reference <path-or-url-to-any-independent-quran-dataset>
```

The build is deterministic. Same inputs give the same outputs and the same hashes, every time.

## Sources and verifying references

This dataset is built on public domain Quran text plus openly licensed structural metadata, and it is checked against independent authorities.

- Arabic Uthmani text, the Tanzil Project, reviewed by Hafiz Husain Al Awjy and distributed through the King Fahd Glorious Quran Printing Complex, CC BY 3.0, https://tanzil.net
- Structural metadata for surahs, juz, hizb, manzil, ruku, page, and sajda, the Tanzil `quran-data.xml`, CC BY 3.0, https://tanzil.net/res/text/metadata/quran-data.xml
- The canonical structure of 114 surahs and 6236 ayahs, the King Fahd Glorious Quran Printing Complex.
- An independent, separately published Quran dataset, used only as a second opinion for the letter level cross check.

Full attribution is in [NOTICE.md](NOTICE.md).

## License

This dataset and everything original in it are released under Creative Commons Attribution 4.0 International, CC BY 4.0. You may copy, share, adapt, and build on it, for any purpose including commercial, as long as you give appropriate credit.

The underlying Arabic Quran text is public domain. The specific source edition and the structural metadata come from the Tanzil Project under CC BY 3.0, so keep the Tanzil attribution in [NOTICE.md](NOTICE.md) when you redistribute. The original schema, the computed metrics, the validation code, and this documentation are CC BY 4.0 by Mirza Iqbal.

See [LICENSE](LICENSE) for the full text.

## Author

Built and maintained by Mirza Iqbal, [github.com/mjmirza](https://github.com/mjmirza).
