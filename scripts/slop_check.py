#!/usr/bin/env python3
"""slop_check.py — score text 0-100 against AI-slop guidelines.

Checks derived from:
  - Charlie Guo, "The Field Guide to AI Slop" (2025): stylistic tics,
    formatting patterns, monotony, filler.
  - Russell et al., "StoryScope" (2026): structural tells — thematic
    over-explanation, embodied-emotion performativity, missing specificity,
    tidy endings.
  - Akinwande et al. (IJCI 2024): average word length is the single
    strongest AI/human classifier feature (AI ~4.97 chars, human ~4.39).
  - Desaire et al. (2023, 99%+ accuracy): equivocal words (but/however/
    although/because) mark humans; vague group nouns mark AI; humans vary
    paragraph length (stddev of paragraph words alone = AUC 0.98), write
    both <11-word and >34-word sentences, and use ? ( ) ; : freely.
  - Georgiou (BDCC 2026) rapid review: surface tells alone are evadable;
    structural and lexical layers must be checked together.
  - Terčon & Dobrovoljc (2026) survey of 44 studies: some cues are
    consistent (low diversity, repetition, impersonal register), others
    flip by genre/model — so register-conditional checks, not absolutes.
  - O'Sullivan (2025): humans disperse in style-space; each LLM forms a
    tight cluster (GPT-4 tighter than 3.5). Uniform rule-following is
    itself a fingerprint — hence the multi-file house-style audit.
  - Etaat (2026): cue directions depend on the human reference population;
    topic vocabulary is forced, style vocabulary is chosen — hence topic
    words (repeated 3+ times) are excluded from word-length/nominal stats.

Register: pass --register formal for reports, postmortems, legal or
condolence writing. It relaxes the checks whose evidence is
register-conditional (contractions, word length, nominalizations, lone
short-fragment sentences). Hard bans stay hard in every register.

House-style audit: pass 2+ files to score each AND get a cross-piece
skeleton report (shared openers, enders, repeated distinctive phrases).

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
    oneword = []
    lens = [word_count(s) for s in sents]
    for i, s in enumerate(sents):
        # (c) one-word drama fragment: "Revolutionary." "Silence." "Everything."
        #     Skip sign-offs (a bare name has no terminal .!?) and price/number
        #     labels ("₹650.", "$40") which are structural, not rhetorical.
        #     Tracked separately: a single lone one-worder is "sparingly, with
        #     intention" territory; stacks and repeats are the reflexive tell.
        if lens[i] == 1 and re.search(r"[.!?]\s*$", s) \
                and not re.match(r"^[₹$€£]?[\d.,]+[.!?]?$", s.strip()):
            oneword.append("one-word sentence ('%s')" % s.strip())
        # (d) two-beat fragment stack: two consecutive sentences <=3 words
        #     each. Greetings/signoffs ("With love, Anika") aren't beats.
        _signoff = re.compile(
            r"^(hi|hey|hello|dear|thanks|thank you|best|cheers|regards|"
            r"warm|kind|with (?:love|thanks|gratitude)|yours|sincerely|see you)\b", re.I)
        if i + 1 < len(sents) and lens[i] <= 3 and lens[i + 1] <= 3 \
                and not _signoff.match(sents[i].strip()) \
                and not _signoff.match(sents[i + 1].strip()):
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
    def dedup(xs):
        seen, out = set(), []
        for h in xs:
            if h not in seen:
                seen.add(h)
                out.append(h)
        return out
    return dedup(hits), dedup(oneword)


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

EQUIVOCAL_RE = re.compile(
    r"\b(?:but|however|although|though|because|yet|except|unless)\b", re.I)

VAGUE_GROUP_PATTERNS = [
    r"\b(?:many|some|most|several|countless)\s+(?:people|experts|researchers|"
    r"professionals|users|individuals|studies|entrepreneurs|leaders)\b",
    r"\bexperts\s+(?:agree|say|believe|suggest|recommend|warn)\b",
    r"\bresearchers\s+(?:say|believe|suggest|have\s+found|agree)\b",
    r"\bstudies\s+(?:show|suggest|have\s+shown)\b",
    r"\bothers\s+(?:may|might|argue|believe|say)\b",
    r"\bindividuals\b",
    r"\bit\s+is\s+widely\s+(?:known|believed|accepted|recognized)\b",
    r"\bpeople\s+(?:are\s+)?(?:increasingly|often)\s+(?:turning|looking|realizing)\b",
]

CONTRACTION_RE = re.compile(
    r"(?i)\b(?:\w+n't|it's|that's|there's|here's|what's|who's|let's|i'm|i've|"
    r"i'll|i'd|you're|you've|you'll|you'd|we're|we've|we'll|we'd|they're|"
    r"they've|they'll|she's|he's|she'll|he'll|she'd|he'd)\b"
)


# ---------------------------------------------------------------- checks

def run_checks(doc, fmt, register="casual"):
    """Returns list of dicts: id, name, points, earned, evidence, applicable.

    register="formal" relaxes the register-conditional checks (contractions,
    word length, nominalizations, lone one-word sentences) whose direction
    flips with genre in the research. Hard bans are register-independent."""
    results = []
    raw, prose, sents = doc.raw, doc.prose, doc.sentences
    W = max(doc.words, 1)

    # Topic vocabulary (content words repeated 3+ times) is forced by the
    # subject, not chosen as style; exclude it from lexical-register stats
    # so a post about "certificate rotation" isn't punished for its topic.
    _low_all = re.findall(r"(?<![A-Za-z])[a-z][a-z'\-]*", prose)
    _freq = {}
    for w in _low_all:
        base = re.sub(r"[^a-z]", "", w)
        if len(base) > 2 and base not in STOP:
            _freq[base] = _freq.get(base, 0) + 1
    topic_words = {w for w, c in _freq.items() if c >= 3}

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

    # -- 10b parallel / staccato repetition. One lone one-word sentence is a
    # deliberate device (free in formal register, cheap elsewhere); repeats
    # and the other five forms are the reflexive tell.
    par_hits, oneword_hits = detect_parallel(sents)
    free_ow = 1 if register == "formal" else 0
    eff = len(par_hits) + max(0, len(oneword_hits) - free_ow) * (
        0.5 if len(oneword_hits) - free_ow == 1 else 1.0)
    if eff == 0:
        ratio = 1.0
    elif eff <= 0.5:
        ratio = 0.8
    elif eff <= 1:
        ratio = 0.3
    else:
        ratio = 0.0
    add("parallel", "No parallel/staccato repetition", 6, ratio,
        evidence(par_hits + oneword_hits))

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

    # -- 19 short + long sentence present. Desaire: humans write <11-word AND
    # >34-word sentences; full credit needs a genuine long one (>=30 words).
    if doc.prose_words >= 120 and len(sents) >= 6:
        lens = [word_count(s) for s in sents]
        has_short = min(lens) <= 5
        long_part = 0.5 if max(lens) >= 30 else (0.25 if max(lens) >= 23 else 0.0)
        ratio = (0.5 * has_short) + long_part
        ev = []
        if not has_short:
            ev.append("no sentence of <=5 words")
        if long_part < 0.5:
            ev.append("longest sentence %d words (want one >=30)" % max(lens))
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

    # -- 21 paragraph variety. Desaire: stddev of paragraph word-counts alone
    # separates human from AI documents at AUC 0.98 — the strongest single
    # structural stat known. Measured as CV of words-per-paragraph.
    if fmt != "social" and len(doc.paragraphs) >= 4:
        pw = [word_count(p) for p in doc.paragraphs]
        mean_pw = statistics.mean(pw)
        pcv = statistics.stdev(pw) / mean_pw if mean_pw > 0 else 0
        if pcv >= 0.40:
            ratio = 1.0
        elif pcv >= 0.28:
            ratio = 0.7
        elif pcv >= 0.18:
            ratio = 0.3
        else:
            ratio = 0.0
        add("paravar", "Paragraph lengths vary (word-count CV)", 6, ratio,
            "paragraph word-counts %s, CV %.2f (want >= 0.40)" % (pw, pcv)
            if ratio < 1 else "")
    else:
        add("paravar", "Paragraph lengths vary (word-count CV)", 6, 1.0, "",
            applicable=False)

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

    # -- 23 contractions. Register-conditional: natural in casual prose,
    # legitimately absent in reports, legal text, and formal documents.
    if register == "formal":
        add("contractions", "Contractions used naturally", 4, 1.0, "",
            applicable=False)
    else:
        nc = len(CONTRACTION_RE.findall(prose))
        need = 1 if (fmt == "cover" or doc.prose_words < 150) else max(1, doc.prose_words // 150)
        ratio = 1.0 if nc >= need else (0.5 if nc >= 1 else 0.0)
        add("contractions", "Contractions used naturally", 4, ratio,
            "%d contractions (want >= %d)" % (nc, need) if ratio < 1 else "")

    # -- 24 somatic emotion performance
    hits = find_all(SOMATIC_PATTERNS, raw)
    add("somatic", "Feelings named, not performed through the body", 4,
        1.0 if not hits else 0.0, evidence(hits))

    # -- 25 average word length (Akinwande 2024: top classifier feature,
    # importance 0.47 — AI ~4.97 chars/word, human ~4.39; direction is
    # register-conditional per Terčon/Dobrovoljc, so formal relaxes it).
    # Measured on lowercase tokens (proper nouns excluded) minus topic words.
    low_words = [w for w in re.findall(r"(?<![A-Za-z])[a-z][a-z'\-]*", prose)
                 if re.sub(r"[^a-z]", "", w) not in topic_words]
    if doc.prose_words >= 40 and len(low_words) >= 25:
        awl = (sum(len(re.sub(r"[^a-z]", "", w)) for w in low_words)
               / len(low_words))
        full, half = (4.95, 5.15) if register == "formal" else (4.65, 4.85)
        if awl <= full:
            ratio = 1.0
        elif awl <= half:
            ratio = 0.5
        else:
            ratio = 0.0
        add("wordlen", "Short words, not latinate inflation", 8, ratio,
            "avg word length %.2f chars excl. topic words (want <= %.2f)"
            % (awl, full) if ratio < 1 else "")
    else:
        add("wordlen", "Short words, not latinate inflation", 8, 1.0, "",
            applicable=False)

    # -- 26 equivocal texture (Desaire 2023: 'but', 'however', 'although',
    # 'because' are each individually human-elevated; AI states, humans
    # qualify and connect).
    if doc.prose_words >= 120:
        neq = len(EQUIVOCAL_RE.findall(prose))
        add("equivocal", "Qualifies and concedes (but/because/although)", 4,
            1.0 if neq >= 1 else 0.0,
            "zero equivocal connectives in %d words; humans concede and"
            " reverse" % doc.prose_words if neq == 0 else "")
    else:
        add("equivocal", "Qualifies and concedes (but/because/although)", 4,
            1.0, "", applicable=False)

    # -- 27 vague crowd attribution (Desaire 2023: ChatGPT cites ambiguous
    # groups — 'others', 'researchers' — where humans name the person).
    hits = find_all(VAGUE_GROUP_PATTERNS, prose)
    n = len(hits)
    ratio = 1.0 if n == 0 else (0.4 if n == 1 else 0.0)
    add("vaguegroups", "No vague crowd attributions", 4, ratio, evidence(hits))

    # -- 28 nominalization density. The mechanism behind AI's higher average
    # word length (Akinwande): abstract -tion/-ity/-ment nouns doing the work
    # verbs should ("the migration required organizational effort" vs "moving
    # took a weekend"). Calibrated: human-sounding drafts run 0-3.5 per 100
    # words, generic slop 4-5, de-surfaced AI prose 15+.
    if doc.prose_words >= 60:
        nom = [n for n in re.findall(
            r"\b[a-z][a-z'\-]*(?:tion|sion|ment|ness|ity|ance|ence)s?\b",
            prose.lower()) if re.sub(r"s$", "", n) not in topic_words
            and n not in topic_words]
        nom_density = len(nom) * 100.0 / doc.prose_words
        t1, t2, t3 = (6.0, 8.0, 12.0) if register == "formal" else (3.5, 5.0, 8.0)
        if nom_density <= t1:
            ratio = 1.0
        elif nom_density <= t2:
            ratio = 0.5
        elif nom_density <= t3:
            ratio = 0.2
        else:
            ratio = 0.0
        add("nominal", "Verbs over abstract -tion/-ity nouns", 5, ratio,
            "%.1f nominalizations per 100 words excl. topic words (want <= %.1f): %s"
            % (nom_density, t1, ", ".join(sorted(set(nom))[:6]))
            if ratio < 1 else "")
    else:
        add("nominal", "Verbs over abstract -tion/-ity nouns", 5, 1.0, "",
            applicable=False)

    # -- 29 punctuation range (Desaire 2023: humans use ? ( ) ; : more; AI
    # writes wall-to-wall commas and periods). Em dash stays banned.
    if doc.prose_words >= 150:
        npunct = sum(prose.count(c) for c in "?(;:")
        add("punctrange", "Uses human punctuation (? parens ; :)", 3,
            1.0 if npunct >= 1 else 0.0,
            "no ?, (, ; or : anywhere in %d words" % doc.prose_words
            if npunct == 0 else "")
    else:
        add("punctrange", "Uses human punctuation (? parens ; :)", 3,
            1.0, "", applicable=False)

    return results


def score(results):
    app = [r for r in results if r["applicable"]]
    total = sum(r["points"] for r in app)
    earned = sum(r["earned"] for r in app)
    return round(earned * 100.0 / total, 1) if total else 0.0


def house_style_audit(docs, names):
    """Cross-piece skeleton report (O'Sullivan 2025: uniform habits across
    pieces are their own fingerprint). Warns when most pieces share a
    structural move or reuse a distinctive phrase."""
    n = len(docs)
    warns = []

    def content_sents(d):
        # skip greeting/signoff-ish one-liners for opener/ender analysis
        return [s for s in d.sentences
                if word_count(s) >= 2 and not re.match(
                    r"^(hi|hey|hello|dear|subject|with love|best|regards|thanks)\b",
                    s, re.I)]

    openers_digit = enders_short = 0
    first_words = []
    for d in docs:
        cs = content_sents(d)
        if not cs:
            continue
        if re.search(r"\d", cs[0]):
            openers_digit += 1
        if word_count(cs[-1]) <= 6:
            enders_short += 1
        m = re.match(r"[\"'“]?([\w']+)", cs[0])
        if m:
            first_words.append(m.group(1).lower())
    if n >= 3 and openers_digit / n > 0.6:
        warns.append("%d/%d pieces open on a number/date detail — a good move "
                     "becoming a signature" % (openers_digit, n))
    if n >= 3 and enders_short / n > 0.6:
        warns.append("%d/%d pieces end on a short punchy beat (<=6 words) — "
                     "vary the exits" % (enders_short, n))
    for w in set(first_words):
        if first_words.count(w) >= max(2, n // 2 + 1) and w not in ("i", "the"):
            warns.append("multiple pieces open with '%s'" % w)

    # distinctive 3-grams shared across pieces
    grams = {}
    for i, d in enumerate(docs):
        toks = [t.lower() for t in re.findall(r"[a-z][a-z'\-]*", d.prose.lower())]
        seen = set()
        for j in range(len(toks) - 2):
            g = " ".join(toks[j:j + 3])
            ws = g.split()
            if sum(1 for w in ws if w in STOP) >= 3 or g in seen:
                continue
            seen.add(g)
            grams.setdefault(g, set()).add(i)
    shared = sorted((g for g, s in grams.items() if len(s) >= 2),
                    key=lambda g: -len(grams[g]))[:5]
    for g in shared:
        warns.append("phrase '%s' appears in %d pieces (%s)"
                     % (g, len(grams[g]),
                        ", ".join(names[i] for i in sorted(grams[g]))))

    print("\nHOUSE-STYLE AUDIT (%d pieces)" % n)
    if warns:
        for w in warns:
            print("  [VARY] %s" % w)
    else:
        print("  no shared skeletons or repeated phrases detected")


def main():
    ap = argparse.ArgumentParser(description="Score text against AI-slop guidelines")
    ap.add_argument("files", nargs="+",
                    help="text/markdown file(s), or - for stdin; 2+ files "
                         "adds a cross-piece house-style audit")
    ap.add_argument("--format", default="generic",
                    choices=["blog", "social", "email", "cover", "generic"])
    ap.add_argument("--register", default="casual", choices=["casual", "formal"],
                    help="formal relaxes register-conditional checks "
                         "(contractions, word length, nominalizations, lone "
                         "one-word sentences); hard bans stay hard")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args()

    docs, all_out = [], []
    for f in args.files:
        raw = sys.stdin.read() if f == "-" else open(f, encoding="utf-8").read()
        doc = Doc(raw)
        results = run_checks(doc, args.format, args.register)
        pct = score(results)
        docs.append(doc)
        all_out.append({"file": f, "format": args.format,
                        "register": args.register, "words": doc.words,
                        "score": pct, "checks": results})

    if args.json:
        print(json.dumps(all_out if len(all_out) > 1 else all_out[0],
                         indent=2, ensure_ascii=False))
        return

    for out in all_out:
        if len(all_out) > 1:
            print("\n=== %s" % out["file"])
        print("slop_check — format=%s, register=%s, %d words"
              % (out["format"], out["register"], out["words"]))
        print("SCORE: %.1f / 100  (target: >= 90)\n" % out["score"])
        for r in out["checks"]:
            if not r["applicable"]:
                continue
            mark = "PASS" if r["passed"] else ("PART" if r["earned"] > 0 else "FAIL")
            line = "  [%s] %-52s %4.1f/%d" % (mark, r["name"], r["earned"], r["points"])
            print(line)
            if r["evidence"] and not r["passed"]:
                print("         -> %s" % r["evidence"])

    if len(docs) >= 2:
        house_style_audit(docs, [o["file"].split("/")[-1] for o in all_out])


if __name__ == "__main__":
    main()
