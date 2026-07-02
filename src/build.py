#!/usr/bin/env python3
"""
build.py — deterministic builder for the Quran Core Dataset.

Reads two CC BY 3.0 Tanzil source inputs and produces a uniquely structured,
normalized, self-describing dataset in three shapes (nested JSON, flat JSONL,
CSV). Every derived metric (word count, letter count, division assignment,
content hashes) is computed here from the source text, so the build is fully
reproducible and every number is verifiable.

Sources (see data/sources/):
  - tanzil-arabic-uthmani.json  Arabic Uthmani text, Tanzil, CC BY 3.0
  - tanzil-quran-data.xml       structural metadata, Tanzil, CC BY 3.0

Original schema, computed metrics, and this code are CC BY 4.0, Mirza Iqbal.

Usage:
  python3 src/build.py            # builds into data/
  python3 src/build.py --check    # builds in-memory, prints summary, writes nothing
"""

import json
import sys
import hashlib
import unicodedata
import csv
import datetime
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "sources"
OUT = ROOT / "data"

ARABIC_TEXT = SRC / "tanzil-arabic-uthmani.json"
METADATA_XML = SRC / "tanzil-quran-data.xml"

DATASET_NAME = "Quran Core Dataset"
DATASET_VERSION = "1.0.0"
DATASET_AUTHOR = "Mirza Iqbal"
DATASET_LICENSE = "CC BY 4.0"
SCRIPT = "uthmani"

TATWEEL = "ـ"
# The opening basmala, exactly as this Tanzil edition stores it, merged into
# ayah 1 of every surah except At-Tawba (9). Al-Fatiha keeps it as ayah 1.
BASMALA = "بِسمِ ٱللَّهِ ٱلرَّحمٰنِ ٱلرَّحِيمِ"


def sha256(text):
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def count_words(text):
    return len([t for t in text.split() if t.strip()])


def count_letters(text):
    """Base Arabic letters. Every Unicode Letter, minus tatweel and minus the
    nonspacing tashkeel marks (category Mn). Definition documented in README."""
    n = 0
    for ch in text:
        if ch == TATWEEL:
            continue
        if unicodedata.category(ch).startswith("L"):
            n += 1
    return n


def word_list(text):
    return [t for t in text.split() if t.strip()]


def parse_metadata(xml_path):
    root = ET.parse(xml_path).getroot()
    suras = {}
    for s in root.iter("sura"):
        idx = int(s.get("index"))
        suras[idx] = {
            "ayas": int(s.get("ayas")),
            "start": int(s.get("start")),
            "name_arabic": s.get("name"),
            "name_transliteration": s.get("tname"),
            "name_english": s.get("ename"),
            "type": s.get("type"),
            "order": int(s.get("order")),
            "rukus": int(s.get("rukus")),
        }

    # boundary markers, each is the (sura, aya) where the division STARTS
    def markers(tag):
        out = []
        for e in root.iter(tag):
            out.append((int(e.get("index")), int(e.get("sura")), int(e.get("aya"))))
        return out

    juz = markers("juz")
    quarters = markers("quarter")  # 240 hizb-quarters -> hizb = (i-1)//4 + 1
    manzils = markers("manzil")
    rukus = markers("ruku")
    pages = markers("page")
    sajdas = {}
    for e in root.iter("sajda"):
        sajdas[(int(e.get("sura")), int(e.get("aya")))] = {
            "index": int(e.get("index")),
            "type": e.get("type"),
        }
    return suras, juz, quarters, manzils, rukus, pages, sajdas


def build_ordinal_index(suras):
    """Map (sura, aya) -> global 1-based ordinal in mushaf order, using the
    canonical sura start offsets from the metadata."""
    ordinal = {}
    for sidx in range(1, 115):
        start = suras[sidx]["start"]  # 0-based global running index
        for aya in range(1, suras[sidx]["ayas"] + 1):
            ordinal[(sidx, aya)] = start + aya  # 1-based
    return ordinal


def assign_division(marker_list, ordinal, suras):
    """Return dict (sura,aya)->division index, by finding the last marker whose
    global ordinal is <= the ayah's ordinal."""
    # marker global ordinal, sorted
    marks = sorted(
        ((ordinal[(s, a)], idx) for (idx, s, a) in marker_list),
        key=lambda x: x[0],
    )
    result = {}
    # walk every ayah in ordinal order
    for (s, a), ord_val in sorted(ordinal.items(), key=lambda kv: kv[1]):
        # binary-ish linear walk: find greatest mark ordinal <= ord_val
        cur = marks[0][1]
        for m_ord, m_idx in marks:
            if m_ord <= ord_val:
                cur = m_idx
            else:
                break
        result[(s, a)] = cur
    return result


def main():
    check_only = "--check" in sys.argv

    quran = json.loads(ARABIC_TEXT.read_text(encoding="utf-8"))
    verses = quran["verses"]
    suras, juz_m, quarter_m, manzil_m, ruku_m, page_m, sajdas = parse_metadata(
        METADATA_XML
    )
    ordinal = build_ordinal_index(suras)

    juz_of = assign_division(juz_m, ordinal, suras)
    quarter_of = assign_division(quarter_m, ordinal, suras)
    manzil_of = assign_division(manzil_m, ordinal, suras)
    ruku_of = assign_division(ruku_m, ordinal, suras)
    page_of = assign_division(page_m, ordinal, suras)

    total_words = 0
    total_letters = 0
    surahs_out = []

    for sidx in range(1, 115):
        smeta = suras[sidx]
        ayahs_out = []
        s_words = 0
        s_letters = 0
        s_concat = []
        for aya in range(1, smeta["ayas"] + 1):
            key = f"{sidx}:{aya}"
            text = verses[key]["text"]
            wc = count_words(text)
            lc = count_letters(text)
            s_words += wc
            s_letters += lc
            s_concat.append(text)
            q = quarter_of[(sidx, aya)]
            sajda = sajdas.get((sidx, aya))
            ayahs_out.append(
                {
                    "number": aya,
                    "verse_key": key,
                    "global_number": ordinal[(sidx, aya)],
                    "text": text,
                    "words": word_list(text),
                    "counts": {"words": wc, "letters": lc},
                    "juz": juz_of[(sidx, aya)],
                    "hizb": (q - 1) // 4 + 1,
                    "hizb_quarter": q,
                    "manzil": manzil_of[(sidx, aya)],
                    "ruku": ruku_of[(sidx, aya)],
                    "page": page_of[(sidx, aya)],
                    "sajda": (
                        {"type": sajda["type"], "index": sajda["index"]}
                        if sajda
                        else None
                    ),
                    "content_hash": sha256(text),
                }
            )
        total_words += s_words
        total_letters += s_letters
        # Canonical rule: every surah carries the opening basmala except
        # At-Tawba (9). Al-Fatiha keeps it as its own ayah 1. The independent
        # validator confirms this against the actual text.
        has_basmala = sidx != 9
        surah_hash = sha256("\n".join(s_concat))
        surahs_out.append(
            {
                "number": sidx,
                "name_arabic": smeta["name_arabic"],
                "name_transliteration": smeta["name_transliteration"],
                "name_english": smeta["name_english"],
                "revelation": {"type": smeta["type"], "order": smeta["order"]},
                "counts": {
                    "ayahs": smeta["ayas"],
                    "rukus": smeta["rukus"],
                    "words": s_words,
                    "letters": s_letters,
                },
                "juz_span": [juz_of[(sidx, 1)], juz_of[(sidx, smeta["ayas"])]],
                "has_bismillah": has_basmala,
                "content_hash": surah_hash,
                "ayahs": ayahs_out,
            }
        )

    corpus_concat = "\n".join(
        verses[f"{s['number']}:{a['number']}"]["text"]
        for s in surahs_out
        for a in s["ayahs"]
    )
    corpus_hash = sha256(corpus_concat)

    built_at = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    dataset = {
        "dataset": {
            "name": DATASET_NAME,
            "version": DATASET_VERSION,
            "author": DATASET_AUTHOR,
            "license": DATASET_LICENSE,
            "built_at": built_at,
            "script": SCRIPT,
            "language": "ar",
            "structure": "normalized corpus -> surahs -> ayahs",
            "counts": {
                "surahs": 114,
                "ayahs": len(verses),
                "juz": 30,
                "hizb": 60,
                "hizb_quarters": 240,
                "manzils": 7,
                "rukus": 556,
                "pages": 604,
                "sajdas": 15,
                "words": total_words,
                "letters": total_letters,
            },
            "letter_definition": "Unicode Letter category, excluding tatweel (U+0640) and nonspacing tashkeel marks",
            "sources": [
                {
                    "asset": "Arabic Uthmani text",
                    "origin": "Tanzil Project (reviewed by Hafiz Husain Al-Awjy, King Fahd Complex distribution)",
                    "url": "https://tanzil.net",
                    "license": "CC BY 3.0",
                },
                {
                    "asset": "Structural metadata (surah, juz, hizb, manzil, ruku, page, sajda)",
                    "origin": "Tanzil quran-data.xml",
                    "url": "https://tanzil.net/res/text/metadata/quran-data.xml",
                    "license": "CC BY 3.0",
                },
            ],
            "content_hash": corpus_hash,
        },
        "surahs": surahs_out,
    }

    print(
        f"surahs={len(surahs_out)} ayahs={len(verses)} words={total_words} letters={total_letters}"
    )
    print(f"corpus_hash={corpus_hash}")
    print(
        f"bismillah surahs={sum(1 for s in surahs_out if s['has_bismillah'])} (expect 113)"
    )

    if check_only:
        return

    OUT.mkdir(exist_ok=True)
    (OUT / "quran.json").write_text(
        json.dumps(dataset, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # flat JSONL (one ayah per line) and CSV, both derived from the nested form
    flat_rows = []
    for s in surahs_out:
        for a in s["ayahs"]:
            flat_rows.append(
                {
                    "verse_key": a["verse_key"],
                    "surah": s["number"],
                    "surah_name_en": s["name_english"],
                    "surah_name_ar": s["name_arabic"],
                    "surah_name_translit": s["name_transliteration"],
                    "ayah": a["number"],
                    "global_number": a["global_number"],
                    "text": a["text"],
                    "words": a["counts"]["words"],
                    "letters": a["counts"]["letters"],
                    "juz": a["juz"],
                    "hizb": a["hizb"],
                    "hizb_quarter": a["hizb_quarter"],
                    "manzil": a["manzil"],
                    "ruku": a["ruku"],
                    "page": a["page"],
                    "revelation_type": s["revelation"]["type"],
                    "revelation_order": s["revelation"]["order"],
                    "sajda_type": (a["sajda"]["type"] if a["sajda"] else ""),
                    "content_hash": a["content_hash"],
                }
            )

    with (OUT / "quran.jsonl").open("w", encoding="utf-8") as f:
        for r in flat_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    with (OUT / "quran.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(flat_rows[0].keys()))
        w.writeheader()
        w.writerows(flat_rows)

    print(f"wrote {OUT / 'quran.json'} ({(OUT / 'quran.json').stat().st_size} bytes)")
    print(f"wrote {OUT / 'quran.jsonl'} ({len(flat_rows)} rows)")
    print(f"wrote {OUT / 'quran.csv'}")


if __name__ == "__main__":
    main()
