---
name: no-slop
description: Write prose that reads as human, not AI. Use this skill whenever drafting or editing ANY text meant for people to read — blog posts, newsletters, social media posts and captions (LinkedIn, X/Twitter, Instagram), emails, cold outreach, cover letters, bios, About pages, product descriptions, announcements. Also use when the user says text "sounds like AI", asks to "humanize" writing, wants something "more natural" or "less robotic", or mentions AI slop. Built from empirical research on how AI writing differs from human writing; includes a lint script to verify output before delivering.
---

# No Slop

Readers have learned the tells of AI writing. One "it's not X, it's Y" or a stack of emoji bullets and they stop trusting the whole piece — even if a human wrote it. This skill exists because the tells are now documented and measurable: a 2026 study of 61,608 stories found AI writing detectable at 93% accuracy from *structural* choices alone, even after the surface style was edited to look human. Another separated ChatGPT from working scientists at over 99% document-level accuracy using twenty countable features: paragraph variance, sentence variance, question marks, and the words "but" and "because". So fixing word choice isn't enough. You have to write differently at three layers:

1. **Surface tics** — phrases, punctuation, formatting habits. Easy to ban, and banned below.
2. **Structural habits** — over-explaining the point, tidy resolutions, abstraction instead of specifics, uniform rhythm. The deeper fingerprint; takes deliberate effort to break.
3. **Distributional narrowness** — the deepest one. In stylometric space, humans form broad scattered clusters; every LLM forms a tight one, and *more polished models cluster tighter*. A fixed bag of tricks applied identically to every piece is detectable even when each piece looks fine alone. The antidote isn't more rules; it's variation and situational fit.

That third layer is why this skill is mostly dials, not laws. The hard bans are few and truly absolute; everything else moves with the situation.

## Situate first

Before any rule, answer three questions. They set every dial below.

1. **Who is writing, to whom?** A founder to customers, a friend to a friend, an engineer to execs, a stranger asking for something. The relationship sets how much warmth, slang, and self-reference fits.
2. **What's at stake for the reader?** Grief, money, their time, mild entertainment. High stakes shrink playfulness to zero; low stakes make stiffness the tell.
3. **What register does the moment expect?** Casual (posts, most emails, captions), professional-warm (cover letters, announcements, work email), or formal (reports, postmortems, legal-ish, condolences). Match it. AI's signature drift is toward formal-neutral-impersonal *regardless of the moment* — in a study of L2 learners, GPT-4 stayed measurably more formal and complex even when explicitly prompted to write simply. Overshooting casual is just the mirror-image failure: forced breeziness in a serious note reads as fake as corporate padding in a tweet.

How the register moves the dials:

| Dial | Casual | Professional-warm | Formal / serious |
|---|---|---|---|
| Contractions | everywhere | everywhere | optional; whatever reads sincere |
| Word length / abstraction | short words, verbs | short words, some field terms | field vocabulary is fine; padding still isn't |
| Feelings | named plainly | named, briefer | restraint is honest; don't perform warmth |
| Jokes, asides, digressions | one is a signature | maybe one, small | usually none |
| Punchy fragments | sparingly | sparingly | one sincere beat at most ("Truly.") |
| Lint invocation | default | default | `--register formal` |

**Precedence rule:** hard bans always apply. Every other guideline is a dial, and the situation outranks the dial's default. If following a rule would make the piece worse for its actual reader — a contraction quota in a legal notice, a forced digression in a three-line email, a "concrete opener" in a condolence — the situation wins. Note it and move on; don't contort the piece to satisfy a check.

## Before you draft

**1. Collect real specifics.** Human writing names names — real products, prices, dates, places, people, titles — at roughly twice the rate of AI writing. Before drafting, list every concrete detail available from the user's request and context. Those details are the skeleton of the piece; abstractions are packing foam.

- If the user gave you specifics, use them nearly all.
- **The prove-it test.** You're writing in the user's name. Before adding any detail, ask: could a reader ask the user to back this up? If yes and it didn't come from the user's input, cut it. This covers far more than metrics: an invented friend, a named train line, a client incident, a "here's what worked" finding, a family anecdote — these are fabrications even though they feel exactly like the specificity this skill demands. A fabricated detail reads perfectly human right up until someone asks about it in a reply or an interview. This includes claims about the user's own actions and research — "I looked through your Instagram before writing this" is a fabrication if the user never said they did, even though it sounds like diligence rather than invention. Public facts (a real product's real behavior, a well-known event) are fair game if accurate; the user's *life and actions* are not yours to invent.
- When you can ask the user, ask — one real detail from them beats three plausible ones from you. When you must deliver without asking, use only what's given and let the piece be shorter. Fewer, truer details beat rich fake ones.
- If the prompt has almost no specifics (a "thoughts on X" post), don't compensate by inventing experiences. Compensate with a point of view: opinions, preferences, and observations are yours to write because the user can own or edit them; events are not.

**2. Decide the one thing the piece says.** Then plan to never state it as a lesson. AI narrators spell out the theme 77% of the time; human writers 52%. The reader should be able to say what the piece was about; the text shouldn't say it for them.

**3. Pick an entry point past the beginning.** Humans start mid-scene, mid-thought, mid-argument. AI starts with setup ("In today's digital landscape...") or a definition. Open with the most specific interesting thing you have — a moment, a number, an objection, a mistake.

## Voice rules

**Name feelings plainly.** This is the single most counterintuitive finding: AI conveys emotion through bodies and atmosphere ("my chest tightened as I hovered over send") 81% of the time; humans mostly just say the feeling ("I was nervous about sending it"). Showing-not-telling *is the AI tell* now. Say it: "I was annoyed." "I loved it." "It scared me."

**Concrete beats abstract, every time.**
- Slop: "I worked with a client in the food industry to improve their online presence."
- Human: "I rebuilt the website for a bakery in Cork that was losing orders because the menu was a PDF."

**Plain verbs.** Use, make, help, build, fix, run, try. Not leverage, utilize, empower, elevate, streamline, harness, unlock, foster.

**Short words where you have the choice.** Average word length is the single strongest feature machine classifiers use to spot AI text (AI ≈ 5.0 characters per word, human ≈ 4.4 — the top-ranked feature in a 500K-essay study). The gap is abstract Latinate nouns doing verbs' work: functionality, implementation, requirement, considerations. Write the short version when both exist: use not utilize, need not requirement, about not approximately, people not individuals, before not prior to. The nuance: this is about *chosen* style, not topic. "Certificate rotation" in a postmortem and "variegation" in a plant listing are the subject matter; leave them alone (the linter excludes repeated topic words for exactly this reason). The tell is a draft where the abstraction is load-bearing everywhere and no verb survived: "the migration process required a weekend of organizational effort" instead of "moving took a weekend".

**Qualify, concede, reverse.** In the study that separated scientists from ChatGPT at 99% accuracy, four of the twenty features were just the words "but", "however", "although", and "because" — every one a mark of the *human*. AI states everything in one clean direction; people argue with themselves mid-sentence and commit anyway. "The databases are genuinely good, but I stopped trusting the company" is human texture. Treat this as a floor, not a quota: zero but/because/although in 150+ words reads pre-planned, but stacking concessives doesn't make text human — in a study of learner essays, the AI actually out-used "however" and "even though" while the humans just wrote "I think". Which is the companion finding: plain first-person stance markers ("I think", "honestly", "my guess is") are among the most robust human markers in informal writing. Own claims directly instead of dressing them in concession structure. (And "however" is fine; "moreover" and "furthermore" are still slop.)

**Stay involved.** Across 44 studies, the most consistent register finding is that AI drifts impersonal: more nouns and prepositions, fewer first-person pronouns, fewer sensing verbs (read, look, hear, felt), almost no idioms, no irritation, nothing rude. Human writing in informal genres is *involved*: I did, I saw, it felt off, the thing wouldn't die. If a personal piece could be reprinted as a company FAQ without edits, it's not involved enough. This includes negative affect — mild annoyance, a grudge, calling something bad — where the situation earns it.

**Commit to opinions.** Humans have a point of view and are fine being morally messy (ambivalent 59% vs 38% for AI). Don't both-sides everything, don't hedge every claim, don't sand off preferences. "Notion is overkill for notes" beats "Notion, while powerful, may not suit every workflow."

**Talk to the reader when natural.** Humans address the reader directly 4× as often as AI. An occasional "you know the type" or "look —" or a parenthetical aside (like this one) is human. Constant "you" in every sentence is marketing-speak; occasional is conversation.

**Let one thread dangle.** Human writing digresses — a side note, a tangent that half-connects, an admission that doesn't get resolved. AI ties every sentence to the thesis with 79%-no-subplots tidiness. One brief digression per piece is not a flaw; it's a signature. Same for endings: not everything needs resolving.

**Use contractions.** It's, don't, I've, that's. Everywhere, including cover letters. Zero contractions reads as either AI or a legal notice.

## Hard bans

These patterns are individually forgivable but collectively damning. Treat every one as a bug:

| Ban | Example of the violation |
|---|---|
| Contrast scaffold "not X, but Y" | "It's not about the plants — it's about the joy they bring." |
| Rule-of-three snap | "Fast, simple, and reliable." "Think bigger. Act bolder. Move faster." |
| Unearned profundity | "Something shifted." "Everything changed." "But here's the thing." "That's when it hit me." |
| Fake question pivot | "The solution? Simpler than you think." "The result? A 40% increase." |
| Vapid opener | "In today's fast-paced world..." "Have you ever...?" "Picture this:" "We've all been there." "Let's face it." |
| Universal closer | "Whatever your 'ukulele' is — start strumming." "So next time you X, remember Y." "Here's to the dreamers." |
| Moral-of-the-story ending | "Ultimately, it's about connection." "At the end of the day, what matters is..." |
| "No X, no Y — just Z" | "No filters, no gimmicks — just great coffee." |
| Parallel / staccato repetition | See the dedicated section below. Covers "more X, more Y, more Z" triads, "keep your A, keep your B, keep your C", fragment stacks ("Fast. Simple. Done."), echo ("It works. It just works."), sentence-start anaphora ("We build. We ship. We grow."), and one-word drama ("Revolutionary."). |
| Slop lexicon | delve, tapestry, testament to, game-changer, seamless, elevate, unlock, journey (metaphorical), vibrant, nestled, bustling, myriad, plethora, "it's worth noting", "in conclusion", moreover, furthermore |
| Emoji bullets / decoration | "✅ Ship faster 🚀" in an email or blog. Unicode arrows (→), 𝗯𝗼𝗹𝗱 unicode. |
| Random bolding | Bolding a phrase mid-paragraph for fake emphasis. |
| Em dashes | None. Zero. Not one. The em dash (—), the spaced en dash ( – ), and the double hyphen (--) are all banned outright — rewrite with a comma, a period, parentheses, or two sentences. This is stricter than typical style advice on purpose: the em dash is the single most reflexive AI-punctuation tell, so this skill removes it entirely rather than rationing it. |
| Generic metaphor | "Every chord is a puzzle piece that clicks into place." If a metaphor could attach to any topic, cut it. A metaphor must come from the specific world of the piece, or from a real shared reference; otherwise skip metaphors entirely. |
| Vague crowd attribution | "Experts agree...", "Many people find...", "Researchers say...", "Studies show...", "individuals". ChatGPT cites ambiguous groups where humans name the actual person or just own the claim. Name who, or say "I think". |

## Rhythm

AI writes sentences of nearly uniform length in paragraphs of nearly uniform shape. Humans don't. Gary Provost's demonstration is the standard: five-word sentences in a row sound like a drone; music comes from variation. Concretely:

- Any piece over ~120 words needs at least one sentence of five words or fewer and at least one that runs past 30. Humans write 35-word sentences without noticing; AI's cluster between 15 and 25.
- Paragraph lengths must visibly differ *in word count*, not just sentence count. The standard deviation of paragraph length alone identifies AI documents at AUC 0.98 — the single most damning structural stat in the detection literature. Make one paragraph at least double the length of another. A one-sentence paragraph is allowed. Encouraged, even.
- Use the whole punctuation kit. Humans reach for question marks, parentheses, colons, and semicolons far more than AI does; a longer piece with nothing but commas and periods is flying the flag. (The em dash is the one exception and stays banned.)
- Don't start three sentences in a row with the same word (except "I" in personal writing).
- Read the draft aloud in your head. If you can predict each sentence's length from the last one, break the pattern.

One short sentence is a tool; a *pile* of them is a tic. The rule above wants a single genuine short sentence for contrast ("It scared me." "I still open Notion sometimes."). It does not want two or three stacked for drama — that's the next section.

And read the rhythm targets as *dispersion floors*, not a recipe. They exist to force variance into prose that would otherwise flatline. A piece that mechanically ticks every box — one 4-word sentence, one 31-word sentence, one one-liner paragraph, every time — has traded the flatline for a different uniform. Some pieces earn their long sentence; some don't have one, and that's variance too.

## Parallel and staccato repetition

This is the tic that survives every other fix, because it feels like craft while you're doing it. The writer reaches for repetition to manufacture emphasis the sentence hasn't earned. The *rhythm* becomes the point, standing in for an actual one. Humans do this occasionally and on purpose; AI does it reflexively, and readers now clock it instantly. Six forms, all banned:

- **Anaphoric triads** — the same word heading three parallel clauses: "More days mean more clicks, more conversions, and an easier path." / "Keep your structure tight, keep your timelines realistic, and keep your focus sharp." Fix: make the point once, concretely. "More days on the site means more chances to convert" says the whole thing.
- **Fragment stacks** — short sentence fragments lined up for punch: "Fast. Simple. Done." / "No fluff. No filler. No nonsense." Fix: write the actual sentence. "It's fast and it doesn't crash."
- **Echo repetition** — repeating a word or phrase as its own beat: "This changes everything. Everything." / "It works. It just works." Fix: cut the echo. If the first sentence is true, the repeat adds nothing but drama.
- **Sentence-start anaphora** — consecutive sentences opening with the same word: "We build. We ship. We grow." / "You show up. You do the work. You leave." Fix: combine them, or vary the openings so the sentences carry the emphasis instead of the pattern.
- **One-word drama sentences** — a single word dropped in for *manufactured* effect: "Revolutionary." "Silence." "Everything." Fix: attach it to a real clause, or delete it. The exception that proves the rule: one sincere beat in a serious register ("Truly." in a condolence, "Done." confirming a request) is a human device — the tell is drama the content didn't earn, and any second one in the same piece.
- **Rhetorical modifier lists** — the same comparative repeated across items: "faster loads, faster checkout, faster everything." Fix: state the concrete result once.

The tell they share: remove the repetition and the meaning is unchanged, because the repetition was never carrying meaning. If a parallel structure genuinely earns its keep (rare, but it happens), you'll be able to say what each element adds that the others don't. If you can't, it's decoration.

## Structure

- **Default to prose.** Bullets only when the content is genuinely a list (specs, steps, dates). If every section of a blog post is a header plus three bullets, you've written a slide deck.
- **Headers**: a blog post under 800 words needs few or none. Never header-per-paragraph.
- **Middles can wander a little** — see "let one thread dangle" above.
- **Endings: stop early.** End on a concrete detail, a specific plan, a joke, an open question you actually don't answer, or just... stop. The last two sentences must not summarize, moralize, or inspire. If your ending would survive being pasted onto a different article on the same topic, it's not an ending, it's a template. Watch especially for the aphorism close — a final line that would work on a poster ("You can't fix what you're not looking at"). It feels earned because you wrote it, but it's still a moral. If you love the line, move it into the middle and end on the concrete thing that comes after it.

## Don't wear the same disguise twice

The stylometric finding that should worry a skill like this one: humans scatter in style-space, LLMs cluster — and GPT-4 clusters *tighter* than GPT-3.5. Refinement without variation increases detectability. The same applies to this skill's own devices: the concrete-number opener, the wry parenthetical, the short shrug ender ("Just in case."), the "honestly" aside. Each reads human once. Used in every piece, they become a house style a reader (or a classifier) learns in three samples.

So when producing more than one piece — in a session, or for the same user over time:

- Treat the devices in this skill as a palette, not a sequence. Pick a few per piece; leave the rest unused. Occasionally write a piece that uses almost none.
- Vary the skeleton deliberately: if the last piece opened on a number, open this one mid-argument or on a quote or plainly. If the last one ended on a fragment, end this one on a full sentence that just stops.
- Never reuse a distinctive phrase across pieces. "I tried to X" twice in two deliverables is a fingerprint.
- The linter's multi-file mode audits this: `slop_check.py piece1.md piece2.md piece3.md` prints a house-style report of shared openers, enders, and repeated phrases.

The deeper point: rules executed uniformly are what made AI detectable in the first place. Human variance isn't noise on top of the rules; it *is* the signal.

## Formats

Read `references/formats.md` for the format you're writing — it has norms, slop examples, and good examples for each. Two rules about using it: treat the word-count norms as real caps, not vibes — a "60–150 word" format means cut until you're inside it, and shorter usually reads more human anyway. And the examples are calibration, not stock copy: never reuse their lines, jokes, or phrasings in your output, because a skill-example turning up verbatim in real posts is its own kind of slop. Quick reference:

| Format | Length instinct | Biggest risk |
|---|---|---|
| Blog / newsletter | As short as the idea allows | Listicle structure, moral ending |
| LinkedIn | 60–150 words | Vulnerability theater, "Agree?" |
| X / Twitter | One thought | Fake profundity |
| Instagram caption | 1–4 short lines + specifics | Emoji spam, "not just X" |
| Cold email | Under 120 words | Corporate phrases, fake flattery |
| Work email | Answer first, context after | Padding, "I hope this finds you well" |
| Cover letter | 250–350 words | "I am excited to apply", invented metrics |
| Serious note | Short, plain, direct | Mail-merge sympathy; forced breeziness |
| Technical report | Facts, causes, owners | Ownerless passive fog, moralized "learnings" |

## Verify before delivering

Save the draft to a temp file and run the checker (works with plain python3, no dependencies):

```bash
python3 <path-to-this-skill>/scripts/slop_check.py /tmp/draft.md --format blog
python3 <path-to-this-skill>/scripts/slop_check.py /tmp/report.md --format generic --register formal
python3 <path-to-this-skill>/scripts/slop_check.py /tmp/a.md /tmp/b.md   # + house-style audit
```

Formats: `blog`, `social`, `email`, `cover`, `generic`. Use `--register formal` for reports, postmortems, legal-adjacent text, and serious personal notes — it relaxes the checks whose research evidence is register-conditional (contractions, word length, nominalizations, a lone short beat) while keeping every hard ban. Passing multiple files adds the cross-piece house-style audit; run it whenever a session produces two or more pieces.

It scores 0–100 against the research-derived guidelines and lists every violation with evidence. **Target: 90+.** Fix the flags, then rerun; two or three passes is normal. Two qualifications, per the precedence rule above: don't game a flag by thesaurus-swapping a banned word for an equally sloppy synonym — fix the underlying habit (usually: be more specific, or cut the sentence). And if a residual flag is the *register* talking — field vocabulary tripping the word-length check in a technical piece, say — deliver anyway and tell the user which flag you're overriding and why, rather than damaging the piece to appease the number.

If you can't run scripts, check the draft by hand against the Hard bans table plus these eight, which catch most failures:

1. Zero "not X, but Y" constructions, zero fake question pivots.
2. At least 2–3 concrete specifics (names, numbers, places) the reader could verify or picture.
3. Sentence lengths visibly vary; one very short sentence for contrast, but no stacks of them, no fragment triads, no one-word drama, no repeated-word parallel clauses.
4. Feelings named directly, not performed through body language.
5. The ending doesn't state the lesson or universalize.
6. Emoji, bullets, and bold at or near zero for the format — and not a single em dash (—), spaced en dash, or double hyphen anywhere.
7. Words stay short: no clusters of -tion/-ity/-ment abstractions, nothing "utilized", no "individuals". If two long Latinate nouns share a sentence, rewrite it around a verb.
8. In anything over ~120 words: at least one honest "but", "because", or "although"; paragraph lengths visibly unequal; at least one question mark, parenthesis, or colon doing real work; and no "experts agree"-style crowd citations.

When editing someone else's AI-sounding text rather than drafting fresh, read `references/patterns.md` — it has before/after rewrites for every pattern. For the research behind all of this, see `references/research-notes.md`.
