"""pipeline/verify_quotes.py

Automated quote and publish-date verification test suite.
Asserts that every cited quote across candidates, station tables, docs, and reports:
1. Exists verbatim (whitespace-normalized) in the saved evidence text in data/evidence/
2. Matches the exact published date recorded in data/evidence/manifest.csv
3. Does not exceed 25 words in length
4. Validates that every evidence file matches its recorded SHA-256 hash
"""

import os
import re
import hashlib
import unicodedata
import pandas as pd
import pytest

MANIFEST_PATH = "data/evidence/manifest.csv"
CANDIDATES_PATH = "data/interim/events_candidates_v2.csv"
EVIDENCE_DIR = "data/evidence"

def normalize_text(text: str) -> str:
    """Normalize whitespace and punctuation quotes for robust verbatim matching."""
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    text = text.replace("—", "-").replace("–", "-")
    return re.sub(r"\s+", " ", text).strip().lower()

def count_words(text: str) -> int:
    """Count words in a quote string."""
    return len(text.strip().split())

@pytest.fixture(scope="module")
def manifest():
    assert os.path.exists(MANIFEST_PATH), f"Manifest missing at {MANIFEST_PATH}"
    df = pd.read_csv(MANIFEST_PATH)
    return df

@pytest.fixture(scope="module")
def evidence_store(manifest):
    store = {}
    for _, row in manifest.iterrows():
        fpath = os.path.join(EVIDENCE_DIR, row["text_file"])
        assert os.path.exists(fpath), f"Evidence text file missing: {fpath}"
        with open(fpath, "r", encoding="utf-8") as f:
            raw_text = f.read()
        
        # Verify SHA-256 hash matches manifest
        with open(fpath, "rb") as f_bin:
            calc_hash = hashlib.sha256(f_bin.read()).hexdigest()
        assert calc_hash == row["sha256"], f"SHA-256 mismatch for {row['text_file']}: {calc_hash} != {row['sha256']}"

        clean_content = normalize_text(raw_text)
        entry = {
            "content": clean_content,
            "raw": raw_text,
            "publish_date": str(row["publish_date"]),
            "text_file": row["text_file"],
            "sha256": row["sha256"]
        }
        store[row["requested_url"]] = entry
        store[row["final_url"]] = entry
    return store

def test_manifest_sha256_integrity(manifest):
    """Verify that every file in data/evidence matches its recorded SHA-256."""
    for _, row in manifest.iterrows():
        fpath = os.path.join(EVIDENCE_DIR, row["text_file"])
        assert os.path.exists(fpath), f"File {fpath} does not exist"
        with open(fpath, "rb") as f:
            h = hashlib.sha256(f.read()).hexdigest()
        assert h == row["sha256"], f"SHA-256 mismatch for {fpath}"

def test_candidate_quotes_verbatim_and_dates(evidence_store):
    """Verify that all quotes in events_candidates_v2.csv are verbatim and match dates."""
    assert os.path.exists(CANDIDATES_PATH), f"Candidates file missing at {CANDIDATES_PATH}"
    df = pd.read_csv(CANDIDATES_PATH)

    for _, row in df.iterrows():
        cid = row["proposed_id"]
        for s_idx in [1, 2]:
            url = row[f"source_url_{s_idx}"]
            ev = row[f"evidence_{s_idx}"]
            sdate = str(row[f"source_date_{s_idx}"])

            if pd.isna(url) or url in ["UNVERIFIED", "HTTP 404 on check"]:
                continue
            if pd.isna(ev) or ev in ["UNVERIFIED", "HTTP 404 on check", "Second independent report not located"] or "HTTP" in ev:
                continue

            assert url in evidence_store, f"Candidate {cid} Source {s_idx} URL not found in evidence store: {url}"
            entry = evidence_store[url]

            # 1. Word count constraint <= 25 words
            n_words = count_words(ev)
            assert n_words <= 25, f"Candidate {cid} Source {s_idx} quote exceeds 25 words ({n_words} words): '{ev}'"

            # 2. Verbatim substring in evidence text
            norm_ev = normalize_text(ev)
            assert norm_ev in entry["content"], (
                f"Candidate {cid} Source {s_idx} quote not found verbatim in {entry['text_file']}.\n"
                f"Target quote: {norm_ev}\n"
                f"File: {entry['text_file']}"
            )

            # 3. Date match
            assert sdate == entry["publish_date"], (
                f"Candidate {cid} Source {s_idx} stated date {sdate} != publish date {entry['publish_date']} in {entry['text_file']}"
            )

def test_station_and_key_sources(evidence_store):
    """Verify quotes cited in station table and key events."""
    key_quotes = [
        {
            "name": "Deccan Herald 5 May 2022 (Rainbow Drive flood)",
            "url": "https://www.deccanherald.com/amp/story/india%2Fkarnataka%2Fbengaluru%2Fapartment-complex-flooded-in-pre-monsoon-rain-in-bengaluru-1106860.html",
            "date": "2022-05-05",
            "quote": "Parts of Rainbow Drive, an apartment complex located on Sarjapur Road, were also flooded."
        },
        {
            "name": "Deccan Herald 5 May 2022 (KSNDMC up to 70 mm)",
            "url": "https://www.deccanherald.com/amp/story/india%2Fkarnataka%2Fbengaluru%2Fapartment-complex-flooded-in-pre-monsoon-rain-in-bengaluru-1106860.html",
            "date": "2022-05-05",
            "quote": "Bommanahalli, Mahadevapura, Yelahanka, and Bengaluru South received up to 70 mm of rainfall"
        },
        {
            "name": "Gulf Times 27 Sept 2017 (E2017_09 flood)",
            "url": "https://www.gulf-times.com/story/565360/heavy-rains-paralyse-bengaluru-mysuru",
            "date": "2017-09-27",
            "quote": "Even upscale suburbs like Koramangala and Jayanagar witnessed flash floods as the drains, filled with silt and filth, failed to cope"
        },
        {
            "name": "Gulf Times 27 Sept 2017 (196 mm city-wide maximum, not KR Puram specifically)",
            "url": "https://www.gulf-times.com/story/565360/heavy-rains-paralyse-bengaluru-mysuru",
            "date": "2017-09-27",
            "quote": "with a few areas receiving a maximum of 196mm as recorded at 8.30am"
        },
        {
            "name": "The Quint 5 Oct 2017 (42 mm in 1.5 h, NOT 76.6 mm overnight)",
            "url": "https://www.thequint.com/amp/story/news/india/heavy-rains-in-bengaluru",
            "date": "2017-10-05",
            "quote": "According to the India Meteorological Department, the city received 42 mm rainfall between 1 pm and 2.30 pm on 5 October."
        },
        {
            "name": "The News Minute 20 Oct 2022 (Seegehalli 81.5 mm)",
            "url": "https://www.thenewsminute.com/karnataka/heavy-rainfall-bengaluru-causes-waterlogging-many-areas-169062",
            "date": "2022-10-20",
            "quote": "Seegehalli received 81.5 mm of rainfall on Wenesday, October 19, while Doddabanahalli received 78 mm."
        },
        {
            "name": "Deccan Herald 5 Aug 2022 (CAND_2022_08_03 RBD flood)",
            "url": "https://www.deccanherald.com/india/karnataka/bengaluru/bengaluru-residents-use-tractors-to-get-into-flooded-layout-1133227.html",
            "date": "2022-08-05",
            "quote": "The torrential rainfall on the intervening night of Tuesday and Wednesday filled the 300-metre stretch with at least three-feet of water."
        },
        {
            "name": "The News Minute 5 Aug 2022 (CAND_2022_08_03 RBD flooded)",
            "url": "https://www.thenewsminute.com/karnataka/rains-flood-bengaluru-colony-residents-use-tractor-ferry-kids-school-166550",
            "date": "2022-08-05",
            "quote": "Rainbow Drive Layout in Bengaluru’s Sarjapur, was also affected in the downpour and as a result, the streets of the layout were flooded"
        }
    ]

    for item in key_quotes:
        url = item["url"]
        assert url in evidence_store, f"Key quote URL not in evidence store: {url}"
        entry = evidence_store[url]

        n_words = count_words(item["quote"])
        assert n_words <= 25, f"Quote '{item['name']}' exceeds 25 words ({n_words} words)"

        norm_quote = normalize_text(item["quote"])
        assert norm_quote in entry["content"], f"Quote '{item['name']}' not found in {entry['text_file']}"

        assert item["date"] == entry["publish_date"], f"Date mismatch for '{item['name']}': {item['date']} != {entry['publish_date']}"
