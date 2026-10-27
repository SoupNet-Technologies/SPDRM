#!/usr/bin/env python3
"""prose_lint.py — prose style checker for the docs.

Flags banned cliche words, high em-dash density, title-case headings and a few
other patterns this project's docs are held to. Exit code 0 = clean,
1 = blocking hits found. Blocking hits must be rewritten (not deleted).

Usage:
    python3 prose_lint.py README.md [more files...]
    python3 prose_lint.py --json docs/*.md   # machine-readable
"""

import json
import re
import sys
from pathlib import Path

# Words that function as AI connective/promotional tissue. Word-boundary,
# case-insensitive. (words here, not phrases — phrases live in PATTERNS)
BANNED_WORDS = {
    "delve": 2, "delves": 2, "tapestry": 2, "testament": 2, "pivotal": 2,
    "crucial": 2, "showcase": 2, "underscores": 2, "underscore": 2,
    "fosters": 2, "fostering": 2, "interplay": 2, "intricate": 2,
    "intricacies": 2, "vibrant": 2, "garner": 2, "realm": 2,
    "landscape": 2, "journey": 2, "seamless": 2, "seamlessly": 2,
    "game-changer": 2, "cutting-edge": 2, "groundbreaking": 2,
    "breathtaking": 2, "must-visit": 2, "nestled": 2, "boasts": 2,
    "utilize": 1, "utilizing": 1, "leverage": 1,
}

# Phrase-level patterns: (compiled regex, weight, human label)
_PATTERNS = [
    (r"\bnot just\b.{0,60}\bbut\b", 3, "negative parallelism ('not just X but Y')"),
    (r"\bnot only\b.{0,60}\bbut\b", 3, "negative parallelism ('not only X but Y')"),
    (r"\b(is|are) (a|an)? ?(testament|reminder) to\b", 3, "significance inflation"),
    (r"\bserves as\b", 3, "copula avoidance ('serves as')"),
    (r"\bstands as\b", 3, "copula avoidance ('stands as')"),
    (r"\bmarks a (pivotal|significant|key) moment\b", 3, "significance inflation"),
    (r"\bin today'?s (world|landscape|society)\b", 3, "cliché opener"),
    (r"\bat the end of the day\b", 3, "cliché ('at the end of the day')"),
    (r"\bit'?s important to note that\b", 2, "filler ('it's important to note')"),
    (r"\blet'?s (dive|explore|break this down|unpack)\b", 3, "signposting"),
    (r"\bhere'?s what you need to know\b", 3, "signposting"),
    (r"\bin conclusion\b", 3, "formulaic conclusion marker"),
    (r"\bthe future looks bright\b", 3, "generic positive conclusion"),
    (r"\bthat'?s okay\.?$", 2, "reassurance kicker ('And that's okay.')"),
    (r"\byou'?re not alone\b", 2, "reassurance kicker"),
    (r"\b(industry|many) (reports|observers|experts) (say|argue|have noted)\b", 2, "vague attribution"),
    (r"\bchallenges and (future )?(prospects|outlook|legacy)\b", 2, "formulaic challenges section"),
    (r"\b(importantly|interestingly|notably|crucially|essentially|ultimately),\b", 2, "adverb sentence-opener"),
    (r"^so,? ", 1, "sentence-opener tic ('So,')"),
    (r"\bi hope this helps\b", 3, "chatbot artifact"),
    (r"\bas of (my )?(last|knowledge|training)\b", 3, "knowledge-cutoff disclaimer"),
    (r"\bgame.?chang(er|ing)\b", 3, "marketing cliché"),
    (r"\bdeep dive\b", 2, "marketing cliché ('deep dive')"),
    (r"\bcircle back\b", 3, "corporate filler"),
    (r"\b navigate (the|these|those) (challenges|complexities|waters)\b", 2, "metaphor filler"),
    (r"[\u201c\u201d\u2018\u2019]", 1, "curly quotes (use straight quotes)"),
    (r"[\U0001F300-\U0001FAFF\u2600-\u27BF]", 2, "emoji"),
    (r"^\s*-\s\*\*[^*]+\*\*:", 2, "bold-header list item"),
    (r"\bit'?s not just\b", 3, "negative parallelism ('it's not just')"),
    (r"\bwhen it comes to\b", 2, "cliché ('when it comes to')"),
    (r"\b(furthermore|moreover)\b", 1, "stiff connective (furthermore/moreover)"),
    (r"\b(ever-|rapidly )?evolving\b", 2, "cliché ('evolving')"),
    (r"\bunleash\b", 2, "marketing cliché ('unleash')"),
    (r"\bembark\b", 2, "cliché ('embark')"),
]

COMPILED = [(re.compile(rx, re.IGNORECASE | re.MULTILINE), w, label)
            for rx, w, label in _PATTERNS]

# Structural checks per file
MIN_SENT_WORDS = 30


def lint_text(text: str):
    """Return (blocking, warnings, stats) for one document."""
    blocking, warnings = [], []

    # 1. banned words
    for word, weight in BANNED_WORDS.items():
        hits = re.findall(rf"\b{re.escape(word)}\b", text, re.IGNORECASE)
        for m in re.finditer(rf"\b{re.escape(word)}\b", text, re.IGNORECASE):
            line = text[: m.start()].count("\n") + 1
            entry = (line, f"banned word '{word}'", weight)
            (blocking if weight >= 2 else warnings).append(entry)

    # 2. phrase patterns
    for rx, weight, label in COMPILED:
        for m in rx.finditer(text):
            line = text[: m.start()].count("\n") + 1
            entry = (line, label, weight)
            (blocking if weight >= 2 else warnings).append(entry)

    # 3. em dash density (per 1000 words, exclude frontmatter/code)
    body = re.sub(r"^---.*?---", "", text, flags=re.S)
    body = re.sub(r"```.*?```", "", body, flags=re.S)
    words = len(re.findall(r"\b\w+\b", body))
    dashes = body.count("—")
    if words > 0 and (dashes / words * 1000) > 1.5:
        blocking.append((0, f"em dash density {dashes}/{words}w (>1.5/1000)", 2))

    # 4. sentence-length monotony (sampling; heuristic)
    prose = re.sub(r"`[^`]*`|\[.*?\]\(.*?\)|^#{1,6} .*|^> .*", "",
                   body, flags=re.M)
    sentences = [s.split() for s in re.split(r"[.!?]+", prose)
                 if MIN_SENT_WORDS > len(s.split()) > 0]
    lens = [len(s) for s in sentences]
    if len(lens) >= 20:
        stdev = (sum((x - sum(lens)/len(lens))**2 for x in lens) / len(lens)) ** 0.5
        if stdev < 4.5:
            blocking.append((0, f"sentence lengths too uniform (stdev {stdev:.1f} < 4.5)", 2))

    # 5. Title Case headings
    for m in re.finditer(r"^(#{1,6}) (.+)$", text, re.M):
        title = m.group(2)
        content_words = [w for w in re.findall(r"[A-Za-z']+", title)
                         if w.lower() not in {"a", "an", "the", "of", "and",
                                              "in", "on", "to", "for", "with",
                                              "is", "are", "it"}]
        if len(content_words) > 3 and all(w[0].isupper() for w in content_words):
            line = text[: m.start()].count("\n") + 1
            warnings.append((line, "Title Case heading (use sentence case)", 1))

    stats = {"words": words, "em_dashes": dashes}
    return blocking, warnings, stats


def lint_file(path: Path, as_json=False):
    text = path.read_text(encoding="utf-8")
    blocking, warnings, stats = lint_text(text)
    if as_json:
        return {"file": str(path), "blocking": blocking,
                "warnings": warnings, "stats": stats}
    return blocking, warnings, stats


def main(argv):
    as_json = "--json" in argv
    files = [Path(a) for a in argv[1:] if not a.startswith("--")]
    if not files:
        print(__doc__)
        return 2
    results = []
    for f in files:
        blocking, warnings, stats = lint_file(f, as_json=False)
        results.append({"file": str(f), "blocking": blocking,
                        "warnings": warnings, "stats": stats})
    if as_json:
        print(json.dumps(results, indent=2, default=list))
    else:
        for r in results:
            print(f"\n== {r['file']}  ({r['stats']['words']} words, "
                  f"{r['stats']['em_dashes']} em dashes)")
            if not r["blocking"] and not r["warnings"]:
                print("   clean ✔")
            for line, label, _ in sorted(r["blocking"]):
                print(f"   BLOCK  L{line}: {label}")
            for line, label, _ in sorted(r["warnings"]):
                print(f"   warn   L{line}: {label}")
        all_blocking = sum(len(r["blocking"]) for r in results)
        print(f"\n{len(files)} file(s): {all_blocking} blocking hit(s)")
    return 1 if any(r["blocking"] for r in results) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
