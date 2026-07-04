#!/usr/bin/env python3
"""slop_check.py — score text 0-100 against AI-slop guidelines.

Checks derived from:
  - Charlie Guo, "The Field Guide to AI Slop" (2025): stylistic tics,
    formatting patterns, monotony, filler.
  - Russell et al., "StoryScope" (2026): structural tells — thematic
    over-explanation, embodied-emotion performativity, missing specificity,
    tidy endings.

Usage:
  python3 slop_check.py DRAFT.md --format blog|social|email|cover|generic [--json]

Score >= 90 means the text passes the human-writing bar. Every failed check
prints evidence so the writer can fix the exact spot. Checks that don't apply
to a format or length are excluded from the denominator (not free passes).

Stdlib only. Python 3.8+.
"""

import argparse
import json
import re
import statistics
import sys

# ---------------------------------------------------------------- text prep

COMMON_SENTENCE_STARTERS = {
    "The", "A", "An", "I", "It", "We", "You", "They", "He", "She", "But",
    "And", "So", "If", "In", "On", "At", "For", "To", "My", "Our", "Your",
    "This", "That", "There", "Here", "When", "What", "Who", "How", "Why",
    "Not", "No", "Yes", "Then", "Now", "After", "Before", "While", "Because",
    "Most", "Some", "Every", "One", "Two", "Three", "First", "Last", "Next",
    "Even", "Just", "Still", "Also", "Or", "As", "By", "With", "From", "Of",
    "Do", "Did", "Does", "Is", "Are", "Was", "Were", "Have", "Has", "Had",
    "Will", "Would", "Can", "Could", "Should", "May", "Might", "Let", "Its",
    "Their", "His", "Her", "These", "Those", "Each", "All", "Any", "Both",
    "Over", "Under", "Since", "Until", "Once", "Twice", "Maybe", "Perhaps",
    "Please", "Thanks", "Thank", "Hi", "Hey", "Hello", "Dear", "Best",
    "Sincerely", "Regards", "Subject", "Side", "Note", "Ps", "PS",
}

ABBREVS = ["e.g.", "i.e.", "etc.", "vs.", "Mr.", "Ms.", "Mrs.", "Dr.", "St.",
           "Jr.", "Sr.", "approx.", "no.", "No.", "Rs."]


def split_sentences(text):
    text = re.sub(r"\s+", " ", text).strip()
    for abbr in ABBREVS:
        text = text.replace(abbr, abbr.replace(".", "∩"))
    parts = re.split(r"(?<=[.!?])\s+", text)
    out = []
    for p in parts:
        p = p.replace("∩", ".").strip()
        if len(re.findall(r"[A-Za-z0-9]", p)) >= 2:
            out.append(p)
    return out


def word_count(text):
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9''\-]*", text))


class Doc:
    def __init__(self, raw):
        self.raw = raw
        prose_lines, bullets, headers = [], [], []
        for ln in raw.splitlines():
            s = ln.strip()
            if not s:
                prose_lines.append("")
            elif re.match(r"^#{1,6}\s", s):
                headers.append(s)
                prose_lines.append("")
            elif re.match(r"^([-*•●]|\d+[.)])\s", s) or EMOJI_RE.match(s):
                bullets.append(s)
            else:
                prose_lines.append(s)
        self.headers = headers
        self.bullets = bullets
        prose_text = "\n".join(prose_lines)
        self.paragraphs = [re.sub(r"\s+", " ", p).strip()
                           for p in re.split(r"\n\s*\n", prose_text) if p.strip()]
        self.prose = " ".join(self.paragraphs)
        self.sentences = split_sentences(self.prose)
        self.words = word_count(raw)
        self.prose_words = word_count(self.prose)


# ---------------------------------------------------------------- helpers

def find_all(patterns, text, flags=re.IGNORECASE):
    hits = []
    for pat in patterns:
        for m in re.finditer(pat, text, flags):
            snippet = m.group(0)
            if len(snippet) > 70:
                snippet = snippet[:67] + "..."
            hits.append(snippet.strip())
    return hits


def evidence(hits, cap=4):
    uniq = []
    for h in hits:
        if h not in uniq:
            uniq.append(h)
    shown = "; ".join('"%s"' % h for h in uniq[:cap])
    extra = len(uniq) - cap
    return shown + (" (+%d more)" % extra if extra > 0 else "")


# ---------------------------------------------------------------- pattern data

# Tier A: the reflexive scaffold with an intensifier — zero tolerance.
CONTRAST_HARD = [
    r"\bnot (?:just|only|merely|simply) [^.?!\n]{1,60}?[,;—–-]+\s*(?:but\b|it'?s\b|it is\b|this is\b|that'?s\b)",
    r"\bisn'?t (?:just |only |about |merely )[^.?!\n]{1,50}?[.;,—–-]+\s*[Ii]t'?s\b",
    r"\bit'?s not (?:about |just )?[^.?!\n]{1,50}?[—–,;-]+\s*it'?s\b",
    r"\bless about\b[^.?!\n]{1,50}\bmore about\b",
    r"\b(?:isn|wasn|aren|doesn)'?t (?:just|only|about|merely) [^.?!\n]{1,45}[.!]\s+It'?s\b",
]
# Words that carry rhetorical anaphora weight; possessives/articles excluded on
# purpose ("her keys, her coat, her bag" is normal writing, not slop).
# "no" deliberately omitted: 2-item "no plan, no teacher" is common human
# phrasing; the eggregious "no fluff. no filler. no nonsense." lands as a
# fragment stack instead.
ANAPHORA_MODIFIERS = (
    "more|less|fewer|every|better|bigger|faster|stronger|smarter|harder|"
    "deeper|higher|greater|cheaper|easier|louder|bolder|richer|wider"
)
STOP = {
    "the", "a", "an", "and", "or", "but", "so", "to", "of", "in", "on", "for",
    "it", "is", "was", "i", "you", "we", "he", "she", "they", "that", "this",
    "as", "at", "by", "be", "just", "its", "it's", "with", "not", "no",
}


def detect_parallel(sents):
    """Staccato / parallel-repetition tells: in-sentence anaphoric triads,
    repeated rhetorical modifiers across list items, one-word drama fragments,
    two-beat fragment stacks, and echo repetition. Returns evidence strings."""
    hits = []

    # (a) in-sentence anaphoric triad: 3+ comma/semicolon segments sharing a
    #     head word, e.g. "keep your X, keep your Y, and keep your Z".
    for s in sents:
        segs = [x.strip() for x in re.split(r"[;,]", s) if x.strip()]
        if len(segs) < 3:
            continue
        heads = []
        for seg in segs:
            seg = re.sub(r"^(?:and|or|but|then|so|yet)\s+", "", seg, flags=re.I)
            m = re.match(r"([\w']+)", seg)
            if m:
                heads.append(m.group(1).lower())
        for h in set(heads):
            if h and h not in STOP and heads.count(h) >= 3:
                hits.append(("anaphoric triad ('%s ... %s ... %s ...')"
                             % (h, h, h)))
                break

    # (b) repeated rhetorical modifier across adjacent list items:
    #     "more clicks, more conversions", "faster loads, faster checkout".
    joined = " \n".join(sents)
    for m in re.finditer(r"\b(%s)\s+[\w']+,\s+\1\b" % ANAPHORA_MODIFIERS,
                         joined, re.IGNORECASE):
        hits.append("repeated modifier list ('%s')" % m.group(0)[:40].strip())

    # (f) cross-sentence anaphora: 3+ consecutive sentences opening with the
    #     same word ("We build. We ship. We grow."). 'I' excused (narration).
    firsts = []
    for s in sents:
        m = re.match(r"[\"'“]?([\w']+)", s)
        firsts.append(m.group(1).lower() if m else "")
    for i in range(len(firsts) - 2):
        w = firsts[i]
        if w and w != "i" and firsts[i + 1] == w and firsts[i + 2] == w:
            hits.append("sentence-start anaphora ('%s ... %s ... %s ...')"
                        % (w, w, w))

    # sentence-level detectors
    lens = [word_count(s) for s in sents]
    for i, s in enumerate(sents):
        # (c) one-word drama fragment: "Revolutionary." "Silence." "Everything."
        #     Skip sign-offs (a bare name has no terminal .!?) and price/number
        #     labels ("₹650.", "$40") which are structural, not rhetorical.
        if lens[i] == 1 and re.search(r"[.!?]\s*$", s) \
                and not re.match(r"^[₹$€£]?[\d.,]+[.!?]?$", s.strip()):
            hits.append("one-word drama sentence ('%s')" % s.strip())
        # (d) two-beat fragment stack: two consecutive sentences <=3 words each
        if i + 1 < len(sents) and lens[i] <= 3 and lens[i + 1] <= 3:
            hits.append("fragment stack ('%s %s')"
                        % (sents[i].strip(), sents[i + 1].strip()))
        # (e) echo repetition: a short neighbor whose content words are a
        #     subset of the adjacent sentence ("It works. It just works.").
        if i + 1 < len(sents):
            a, b = sents[i], sents[i + 1]
            short, other = (a, b) if lens[i] <= lens[i + 1] else (b, a)
            if word_count(short) <= 4:
                cw_short = {w.lower() for w in re.findall(r"[\w']+", short)
                            if len(w) >= 3 and w.lower() not in STOP}
                cw_other = {w.lower() for w in re.findall(r"[\w']+", other)
                            if w.lower() not in STOP}
                if cw_short and cw_short <= cw_other:
                    hits.append("echo repetition ('%s' / '%s')"
                                % (a.strip()[:30], b.strip()[:30]))
    # de-dup preserving order
    seen, out = set(), []
    for h in hits:
        if h not in seen:
            seen.add(h)
            out.append(h)
    return out


# Tier B: plain cross-sentence contrast — humans use this deliberately; allow one.
CONTRAST_SOFT = [
    r"\b(?:isn|wasn|aren|doesn)'?t [^.?!\n]{1,45}[.!]\s+It'?s\b",
    r"\bnot (?:a|an|the) [^.?!\n]{1,35}[—–;-]+\s*(?:but |it'?s |a |an )",
    r"\b[Tt]hat'?s not [^.?!\n]{1,45}[.!]\s+That'?s\b",
]

PROFUNDITY_PHRASES = [
    r"\bsomething shifted\b", r"\beverything changed\b", r"\bhere'?s the thing\b",
    r"\bhere is the thing\b", r"\bthat'?s when it hit me\b", r"\bthen it hit me\b",
    r"\bit hit me\b", r"\blet that sink in\b", r"\bread that again\b",
    r"\bplot twist\b", r"\bhere'?s the kicker\b", r"\bit clicked\b",
    r"\bthe truth is\b", r"\blet'?s be real\b", r"\blet'?s be honest\b",
    r"\bwhat nobody tells you\b", r"\bnobody talks about\b",
    r"\bnobody warns you\b", r"\bunpopular opinion\b", r"\bhot take\b",
    r"\bgame[- ]changer\b", r"\bchanged everything\b",
]

QUESTION_PIVOT_PATTERNS = [
    r"\bthe (?:result|solution|answer|best part|catch|problem|kicker|outcome|verdict|takeaway|secret|difference|goal|lesson)\?",
    r"\?\s+(?:It'?s |That'?s |Simple\b|Exactly\b|Yes\b|Nope\b|Spoiler\b)",
    r"\bsound familiar\?",
]

VAPID_OPENERS = [
    r"^in today'?s\b", r"^in an era\b", r"^in a world\b", r"^have you ever\b",
    r"^picture this\b", r"^imagine\b", r"^we'?ve all\b", r"^let'?s face it\b",
    r"^it'?s no secret\b", r"^as technology\b", r"^in the fast-paced\b",
    r"^in the age of\b", r"^since the dawn\b", r"^in the world of\b",
    r"^when it comes to\b", r"^are you (?:tired|ready|looking)\b",
    r"^what if i told you\b", r"^ever wonder\b",
]

CLOSER_PATTERNS = [
    r"\bultimately\b", r"\bat the end of the day\b", r"\bin the end\b",
    r"\bwhat matters most\b", r"\bit'?s (?:really |all )?about\b",
    r"\bremember[:,]", r"\bthe lesson\b", r"\bso next time\b",
    r"\bthe next time you\b", r"\bwhatever your\b", r"\bhere'?s to\b",
    r"\bso if you\b", r"\bstart today\b", r"\byou'?ve got this\b",
    r"\bthe possibilities are\b", r"\bi encourage you\b",
    r"\bdon'?t be afraid to\b", r"\btake the leap\b", r"\bin conclusion\b",
    r"\bkeep \w+ing[.!]?\s*$", r"\bwho knows what\b", r"\bthe rest is history\b",
    r"\bwatch this space\b", r"\bstay tuned\b",
]

NO_X_NO_Y = [r"\bno \w+(?: \w+)?, no \w+(?: \w+)?\s*[—–,;-]*\s*just\b"]

LEXICON = [
    r"\bdelv(?:e|es|ing|ed)\b", r"\btapestry\b", r"\btestament to\b",
    r"\brevolutioniz\w+\b", r"\bseamless(?:ly)?\b", r"\beffortless(?:ly)?\b",
    r"\belevat(?:e|es|ing)\b", r"\bunlock(?:s|ing|ed)?\b", r"\bunleash\w*\b",
    r"\bharness(?:es|ing)?\b", r"\bempower\w*\b", r"\bsupercharge\w*\b",
    r"\btransformative\b", r"\bcutting-edge\b", r"\bnext-level\b",
    r"\bfoster(?:s|ing)?\b", r"\bembark\w*\b", r"\brealm\b", r"\bbeacon\b",
    r"\bmyriad\b", r"\bplethora\b", r"\bnestled\b", r"\bbustling\b",
    r"\bvibrant\b", r"\bboasts?\b", r"\bnavigate the\b", r"\bjourney\b",
    r"\bdeep dive\b", r"\bdive deep\b", r"\blook no further\b",
    r"\bwhether you'?re a\b", r"\bit'?s worth noting\b",
    r"\bit is important to note\b", r"\bin summary\b", r"\bmoreover\b",
    r"\bfurthermore\b", r"\bthat being said\b", r"\bneedless to say\b",
    r"\bat its core\b", r"\bthe beauty of\b", r"\belevate your\b",
    r"\bunwavering\b", r"\bmeticulous\w*\b", r"\bunparalleled\b",
    r"\bever-evolving\b", r"\bfast-paced world\b", r"\bdigital landscape\b",
    r"\btreasure trove\b", r"\bgame-changing\b", r"\btop-notch\b",
]

EMAIL_PHRASES = [
    r"\bi hope this (?:email|message) finds you\b", r"\bhope this finds you well\b",
    r"\bi(?:'m| am) reaching out\b", r"\bi wanted to reach out\b",
    r"\btouch base\b", r"\bcircle back\b", r"\bplease do not hesitate\b",
    r"\bdon'?t hesitate to\b", r"\bat your earliest convenience\b",
    r"\bhop on a (?:quick )?call\b", r"\bquick call\b", r"\bbusinesses like yours\b",
    r"\bi'?d love to connect\b", r"\btake your \w+ to the next level\b",
    r"\bonline presence\b", r"\bi came across your\b",
]

COVER_PHRASES = [
    r"\bi am writing to express\b", r"\bexpress my (?:keen |strong )?interest\b",
    r"\b(?:i am|i'?m) (?:excited|thrilled) to apply\b", r"\besteemed\b",
    r"\bproven track record\b", r"\btrack record of success\b",
    r"\bresults[- ]driven\b", r"\bdetail[- ]oriented\b", r"\bteam player\b",
    r"\bfast-paced environment\b", r"\bskill ?set\b", r"\baligns? perfectly\b",
    r"\bperfect fit\b", r"\bhit the ground running\b",
    r"\bwelcome the opportunity\b", r"\bthank you for considering my application\b",
    r"\bvaluable asset\b", r"\bpassionate about\b", r"\bleverage my\b",
    r"\butilize my\b", r"\bdiverse background\b", r"\bwell-positioned\b",
    r"\bi believe (?:that )?my\b", r"\bmake a meaningful (?:impact|contribution)\b",
]

SOCIAL_PHRASES = [
    r"\blet that sink in\b", r"\bread that again\b", r"\bi'?ll wait\b",
    r"\bagree\?", r"\bwho'?s with me\b", r"\bdouble tap\b", r"\bsmash that\b",
    r"\bdrop a \w+ (?:below|in the comments)\b", r"\btag someone\b",
    r"\byou won'?t believe\b", r"\bcalling all\b", r"\bthis one'?s for\b",
    r"\bstop scrolling\b", r"\byour urban jungle\b", r"\bplant parent goals\b",
    r"\btreat yourself\b", r"\bwon'?t last long\b", r"\brun,? don'?t walk\b",
    r"\bdon'?t sleep on\b", r"\btreat your \w+\b", r"\bfill your cart\b",
    r"\bdon'?t miss (?:out|this)\b", r"\byou need this\b",
]

SOMATIC_PATTERNS = [
    r"\bheart (?:raced|racing|pounded|pounding|hammered|sank|sinking)\b",
    r"\bchest tighten\w*\b", r"\bstomach (?:dropped|churned|knotted|flipped)\b",
    r"\bknot (?:formed )?in (?:my|her|his|the) stomach\b",
    r"\bbreath caught\b", r"\bwave of \w+ washed\b", r"\bpalms? (?:were )?sweat\w*\b",
    r"\blump in (?:my|her|his|the) throat\b", r"\bbutterflies in\b",
    r"\bspine tingl\w*\b", r"\bshivers? (?:ran |running )?down\b",
    r"\bpit of (?:my|her|his|the) stomach\b", r"\bblood ran cold\b",
]

EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF️⭐✅❌❤]"
)
DECORATION_RE = re.compile(
    "[→←⇒➔×✦✧"
    "\U0001D400-\U0001D7FF]"
)

CONTRACTION_RE = re.compile(
    r"(?i)\b(?:\w+n't|it's|that's|there's|here's|what's|who's|let's|i'm|i've|"
    r"i'll|i'd|you're|you've|you'll|you'd|we're|we've|we'll|we'd|they're|"
    r"they've|they'll|she's|he's|she'll|he'll|she'd|he'd)\b"
)


# ---------------------------------------------------------------- checks

def run_checks(doc, fmt):
    """Returns list of dicts: id, name, points, earned, evidence, applicable."""
    results = []
    raw, prose, sents = doc.raw, doc.prose, doc.sentences
    W = max(doc.words, 1)

    def add(cid, name, points, ratio, ev="", applicable=True):
        results.append({
            "id": cid, "name": name, "points": points,
            "earned": round(points * max(0.0, min(1.0, ratio)), 2),
            "passed": ratio >= 0.999, "evidence": ev, "applicable": applicable,
        })

    def graded(nhits, allowed=0):
        if nhits <= allowed:
            return 1.0
        if nhits == allowed + 1:
            return 0.5
        return 0.0

    # -- 1 contrast scaffolds
    hard = find_all(CONTRAST_HARD, raw)
    soft = [h for h in find_all(CONTRAST_SOFT, raw) if h not in hard]
    if hard:
        ratio = 0.0
    elif len(soft) > 1:
        ratio = 0.4
    else:
        ratio = 1.0
    add("contrast", "No 'not X, but Y' contrast scaffolds", 10,
        ratio, evidence(hard + (soft if len(soft) > 1 else [])))

    # -- 2 unearned profundity
    hits = find_all(PROFUNDITY_PHRASES, raw)
    add("profundity", "No unearned-profundity beats", 6,
        1.0 if not hits else 0.0, evidence(hits))

    # -- 3 fake question pivots
    hits = find_all(QUESTION_PIVOT_PATTERNS, raw)
    add("qpivot", "No fake question pivots", 4, graded(len(hits), 0), evidence(hits))

    # -- 4 vapid opener
    first_bit = " ".join(sents[:2]).lower() if sents else raw[:200].lower()
    hits = []
    for pat in VAPID_OPENERS:
        m = re.search(pat, first_bit)
        if m:
            hits.append(m.group(0))
    add("opener", "Opening isn't a vapid cliche", 5,
        1.0 if not hits else 0.0, evidence(hits))

    # -- 5 moral/universal ending
    tail_words = re.findall(r"\S+", prose)[-60:]
    tail = " ".join(tail_words)
    hits = find_all(CLOSER_PATTERNS, tail)
    add("ending", "Ending doesn't moralize or universalize", 7,
        1.0 if not hits else 0.0, evidence(hits))

    # -- 6 no x, no y — just z
    hits = find_all(NO_X_NO_Y, raw)
    add("noxnoy", "No 'no X, no Y — just Z'", 3, 1.0 if not hits else 0.0,
        evidence(hits))

    # -- 7 slop lexicon
    hits = find_all(LEXICON, raw)
    n = len(hits)
    ratio = 1.0 if n == 0 else (0.6 if n == 1 else (0.3 if n == 2 else 0.0))
    add("lexicon", "Slop lexicon absent", 8, ratio, evidence(hits))

    # -- 8 format-specific phrases
    fmt_map = {"email": EMAIL_PHRASES, "cover": COVER_PHRASES, "social": SOCIAL_PHRASES}
    if fmt in fmt_map:
        hits = find_all(fmt_map[fmt], raw)
        add("fmtphrase", "Format cliche phrases absent", 8,
            graded(len(hits), 0), evidence(hits))
    else:
        add("fmtphrase", "Format cliche phrases absent", 8, 1.0, "", applicable=False)

    # -- 8b slop saturation: individual tells are forgivable, clusters are
    # damning (Guo). Total phrase-level hits per 100 words across all lists.
    sat_hits = sum(len(find_all(pats, raw)) for pats in [
        CONTRAST_HARD, PROFUNDITY_PHRASES, QUESTION_PIVOT_PATTERNS,
        NO_X_NO_Y, LEXICON, SOMATIC_PATTERNS,
    ]) + (len(find_all(fmt_map[fmt], raw)) if fmt in fmt_map else 0)
    sat_density = sat_hits * 100.0 / W
    if sat_density <= 0.7:
        ratio = 1.0
    elif sat_density <= 1.5:
        ratio = 0.5
    elif sat_density <= 2.5:
        ratio = 0.2
    else:
        ratio = 0.0
    add("saturation", "Tell-density low overall (no clustering)", 8, ratio,
        "%d banned-pattern hits in %d words (%.1f per 100; want <= 0.7)"
        % (sat_hits, W, sat_density) if ratio < 1 else "")

    # -- 9 rhetorical question density
    nq = sum(1 for s in sents if s.endswith("?"))
    allowed_q = max(1, doc.prose_words // 200)
    add("questions", "Rhetorical questions kept rare", 3, graded(nq, allowed_q),
        "%d questions (allowed %d)" % (nq, allowed_q) if nq > allowed_q else "")

    # -- 10 triads
    triad_hits = find_all(
        [r"\b[\w''\-]+, [\w''\-]+,? (?:and|or) [\w''\-]+[.!]"], raw)
    # staccato triple: 3 consecutive sentences of <=4 words
    lens = [word_count(s) for s in sents]
    for i in range(len(lens) - 2):
        if lens[i] <= 4 and lens[i+1] <= 4 and lens[i+2] <= 4:
            triad_hits.append(" / ".join(sents[i:i+3])[:70])
            break
    allowed_t = 1 if doc.words >= 150 else 0
    add("triads", "Rule-of-three not a habit", 5, graded(len(triad_hits), allowed_t),
        evidence(triad_hits))

    # -- 10b parallel / staccato repetition
    par_hits = detect_parallel(sents)
    n = len(par_hits)
    ratio = 1.0 if n == 0 else (0.3 if n == 1 else 0.0)
    add("parallel", "No parallel/staccato repetition", 6, ratio, evidence(par_hits))

    # -- 11 exclamation density
    nex = raw.count("!")
    allowed_ex = 2 if fmt == "social" else max(1, W // 150)
    add("exclaim", "Exclamation marks controlled", 2, graded(nex, allowed_ex),
        "%d exclamation marks (allowed %d)" % (nex, allowed_ex) if nex > allowed_ex else "")

    # -- 12 em dashes: zero tolerance (em dash, spaced en dash, or -- surrogate)
    emd = len(re.findall(r"—|--|\s–\s", raw))
    add("emdash", "No em dashes at all", 6, 1.0 if emd == 0 else 0.0,
        "%d em dash(es) found; use commas, periods, or parentheses" % emd
        if emd else "")

    # -- 13 bold
    nbold = len(re.findall(r"\*\*[^*\n]+\*\*", raw))
    allowed_b = 2 if fmt == "blog" else 0
    add("bold", "No random bolding", 3, graded(nbold, allowed_b),
        "%d bold spans (allowed %d)" % (nbold, allowed_b) if nbold > allowed_b else "")

    # -- 14 bullets
    nb = len(doc.bullets)
    if fmt == "cover":
        allowed_bl = 0
    elif fmt == "social":
        allowed_bl = 2
    elif fmt == "email":
        allowed_bl = 4
    else:
        content_lines = max(1, len([l for l in raw.splitlines() if l.strip()]))
        allowed_bl = max(3, int(content_lines * 0.25))
    add("bullets", "Prose over bullet spam", 4, graded(nb, allowed_bl),
        "%d bullet lines (allowed %d)" % (nb, allowed_bl) if nb > allowed_bl else "")

    # -- 15 headers (blog only)
    if fmt == "blog":
        nh = len(doc.headers)
        allowed_h = max(0, W // 300)
        add("headers", "Headers not listicle-dense", 3, graded(nh, allowed_h),
            "%d headers (allowed %d)" % (nh, allowed_h) if nh > allowed_h else "")
    else:
        add("headers", "Headers not listicle-dense", 3, 1.0, "", applicable=False)

    # -- 16 emoji
    nemo = len(EMOJI_RE.findall(raw))
    allowed_e = 3 if fmt == "social" else 0
    add("emoji", "Emoji within format norms", 4, graded(nemo, allowed_e),
        "%d emoji (allowed %d)" % (nemo, allowed_e) if nemo > allowed_e else "")

    # -- 17 unicode decoration
    dhits = DECORATION_RE.findall(raw)
    add("decoration", "No unicode decoration (arrows, styled bold)", 3,
        1.0 if not dhits else 0.0, evidence(dhits))

    # -- 18 sentence length variation
    if doc.prose_words >= 120 and len(sents) >= 6:
        lens = [word_count(s) for s in sents]
        mean = statistics.mean(lens)
        cv = statistics.stdev(lens) / mean if mean > 0 else 0
        if cv >= 0.45:
            ratio = 1.0
        elif cv >= 0.35:
            ratio = 0.7
        elif cv >= 0.28:
            ratio = 0.3
        else:
            ratio = 0.0
        add("rhythm_cv", "Sentence lengths vary (burstiness)", 8, ratio,
            "coefficient of variation %.2f (want >= 0.45)" % cv if ratio < 1 else "")
    else:
        add("rhythm_cv", "Sentence lengths vary (burstiness)", 8, 1.0, "",
            applicable=False)

    # -- 19 short + long sentence present
    if doc.prose_words >= 120 and len(sents) >= 6:
        lens = [word_count(s) for s in sents]
        has_short = min(lens) <= 5
        has_long = max(lens) >= 23
        ratio = (0.5 * has_short) + (0.5 * has_long)
        ev = []
        if not has_short:
            ev.append("no sentence of <=5 words")
        if not has_long:
            ev.append("no sentence of >=23 words")
        add("range", "Has both punch-short and long sentences", 5, ratio,
            "; ".join(ev))
    else:
        add("range", "Has both punch-short and long sentences", 5, 1.0, "",
            applicable=False)

    # -- 20 same-start runs
    if len(sents) >= 6:
        firsts = [re.match(r"[\"'“]?([\w''\-]+)", s) for s in sents]
        firsts = [(m.group(1).lower() if m else "") for m in firsts]
        run_word, run_len, bad = "", 0, ""
        for w in firsts:
            if w and w == run_word:
                run_len += 1
            else:
                run_word, run_len = w, 1
            limit = 4 if w == "i" else 3
            if run_len >= limit:
                bad = w
                break
        add("samestart", "No monotone sentence-start runs", 3,
            1.0 if not bad else 0.0,
            "%d+ consecutive sentences start with '%s'" % (3 if bad != 'i' else 4, bad) if bad else "")
    else:
        add("samestart", "No monotone sentence-start runs", 3, 1.0, "",
            applicable=False)

    # -- 21 paragraph variety
    if fmt != "social" and len(doc.paragraphs) >= 4:
        pl = [len(split_sentences(p)) for p in doc.paragraphs]
        distinct = len(set(pl))
        ratio = 1.0 if distinct >= 3 else (0.5 if distinct == 2 else 0.0)
        add("paravar", "Paragraph shapes vary", 4, ratio,
            "paragraph sentence-counts %s look uniform" % pl if ratio < 1 else "")
    else:
        add("paravar", "Paragraph shapes vary", 4, 1.0, "", applicable=False)

    # -- 22 specificity density
    tokens = list(re.finditer(r"[A-Za-z0-9][\w''\-]*", prose))
    starts = set()
    for m in re.finditer(r"(?:^|[.!?:\n—]\s*)([A-Z][\w''\-]*)", prose):
        starts.add(m.start(1))
    specific = 0
    for m in tokens:
        t = m.group(0)
        if re.match(r"^\d", t) or re.match(r"^[A-Z]{2,}$", t):
            specific += 1
        elif re.match(r"^[A-Z][a-z]", t) and m.start() not in starts \
                and t not in COMMON_SENTENCE_STARTERS:
            specific += 1
    specific += len(re.findall(r"[₹$€£%]", prose))
    density = specific * 100.0 / max(doc.prose_words, 1)
    if density >= 1.5:
        ratio = 1.0
    elif density >= 0.8:
        ratio = 0.5
    else:
        ratio = 0.0
    add("specificity", "Concrete specifics present (names, numbers, places)", 8,
        ratio, "specificity density %.2f per 100 words (want >= 1.5)" % density
        if ratio < 1 else "")

    # -- 23 contractions
    nc = len(CONTRACTION_RE.findall(prose))
    need = 1 if (fmt == "cover" or doc.prose_words < 150) else max(1, doc.prose_words // 150)
    ratio = 1.0 if nc >= need else (0.5 if nc >= 1 else 0.0)
    add("contractions", "Contractions used naturally", 4, ratio,
        "%d contractions (want >= %d)" % (nc, need) if ratio < 1 else "")

    # -- 24 somatic emotion performance
    hits = find_all(SOMATIC_PATTERNS, raw)
    add("somatic", "Feelings named, not performed through the body", 4,
        1.0 if not hits else 0.0, evidence(hits))

    return results


def score(results):
    app = [r for r in results if r["applicable"]]
    total = sum(r["points"] for r in app)
    earned = sum(r["earned"] for r in app)
    return round(earned * 100.0 / total, 1) if total else 0.0


def main():
    ap = argparse.ArgumentParser(description="Score text against AI-slop guidelines")
    ap.add_argument("file", help="path to text/markdown file, or - for stdin")
    ap.add_argument("--format", default="generic",
                    choices=["blog", "social", "email", "cover", "generic"])
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args()

    raw = sys.stdin.read() if args.file == "-" else open(args.file, encoding="utf-8").read()
    doc = Doc(raw)
    results = run_checks(doc, args.format)
    pct = score(results)

    if args.json:
        print(json.dumps({
            "format": args.format, "words": doc.words, "score": pct,
            "checks": results,
        }, indent=2, ensure_ascii=False))
        return

    print("slop_check — format=%s, %d words" % (args.format, doc.words))
    print("SCORE: %.1f / 100  (target: >= 90)\n" % pct)
    for r in results:
        if not r["applicable"]:
            continue
        mark = "PASS" if r["passed"] else ("PART" if r["earned"] > 0 else "FAIL")
        line = "  [%s] %-52s %4.1f/%d" % (mark, r["name"], r["earned"], r["points"])
        print(line)
        if r["evidence"] and not r["passed"]:
            print("         -> %s" % r["evidence"])


if __name__ == "__main__":
    main()
