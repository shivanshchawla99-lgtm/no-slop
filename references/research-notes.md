# Research Notes

Where the rules come from. Nine sources: two analyzed at creation, four academic papers folded in after the first stress test, three more after the second (which reframed the skill from rules toward register-conditional dials — see the last two sections).

## Source 1: Charlie Guo, "The Field Guide to AI Slop" (Artificial Ignorance, Oct 2025)

A practitioner's taxonomy of AI-writing tells, from surface to content level.

**Red herrings** (commonly cited, NOT reliable): academic vocabulary (delve, unpack, ascertain — professionals use these), perfect grammar (Grammarly exists), absent contractions (may be editing or ESL).

**Stylistic tics** (reliable when frequent):
- Em dashes used indiscriminately. Reddit data showed em-dash usage roughly tripling in a year across tech subreddits.
- Parallelism, especially "It's not X, it's Y" — used reflexively where it adds nothing.
- Snappy triads ("Fast, efficient, and reliable"), unearned profundity ("Something shifted"), mid-sentence questions ("The solution? Simpler than you think"), vapid openers ("In today's fast-paced world").

**Formatting**: random bolding, Unicode decoration (→, ×, 𝗯𝗼𝗹𝗱), emoji-led bullet lists, list-itis (RLHF-driven).

**Structure**: monotony — uniform sentence length, uniform paragraph rhythm, no tense/POV variation. Cites Gary Provost's "vary sentence length" passage as the human counter-example.

**Content**: awkward analogies (plausible, generic, "gesture toward meaning without achieving it" — human metaphors are personally specific or culturally resonant); filler (four sentences doing one sentence's work); surface polish with no coherent throughline ("What did I just read?").

**Key insight**: good human writers use every one of these devices — *sparingly, with intention*. The tell is reflexive frequency. Guo's personal defense: cultivate specificity, particular knowledge, tangible experience, a voice and point of view.

## Source 2: Russell, Rajendhran, Pham, Iyyer, Wieting — "StoryScope" (UMD / Google DeepMind, arXiv 2604.03136, 2026)

Large-scale study: 10,272 human short stories, each mirrored by 5 LLMs (Claude, GPT, Gemini, DeepSeek, Kimi) = 61,608 stories, 304 extracted narrative features. Narrative features ALONE (no style) detect AI at 93.2% macro-F1 — and editing the style out (LAMP artifact-removal) only drops detection 1.6 points. **Structure betrays AI even when the prose is fixed.** Human writing occupies a rarer, more dispersed region of narrative space; the five AI models cluster together.

**The 30 core discriminating features, grouped** (human% vs AI% or 1–5 means):

*AI over-explains themes (thematic over-determination)*:
- Narrator explicitly states the theme: AI 77% vs human 52%
- Thematic explicitness/moralizing: AI 3.94 vs 3.28
- Dialogue as philosophical debate: AI 59% vs 34%
- Vague allusions instead of named references: AI 72% vs 50%

*AI over-writes the body and senses (sensory performativity)*:
- Emotion conveyed through embodiment: AI 81% vs human 38%
- Emotion named with explicit labels: human 29% vs AI 8%
- Smell imagery: AI 82% vs 57%; setting-as-psychological-mirror: AI 4.07 vs 3.58

*AI streamlines structure*:
- No subplots: AI 79% vs human 57%; subplots woven into theme: human 42% vs 21%
- Resolution by protagonist choice: AI 69% vs 46%; internal-acceptance endings: AI 47% vs 27%
- Tighter causal chains (4.20 vs 3.92); humans more comfortable with ambiguous endings

*Humans engage the real world and the reader*:
- Explicit named references to real texts/authors: human 47% vs AI 24%
- Fourth-wall breaks: human 67% vs 39%; direct reader address: human 28% vs 7%

*Humans embrace temporal complexity*:
- More time jumps, flashbacks, nonlinear structure, delayed revelations (all human-elevated)

*Humans are more diverse*:
- More locations, more dialogue relative to narration, morally ambivalent protagonists (59% vs 38%)

**Model fingerprints** (six-way attribution 68.4% F1 from narrative alone): Claude = flat escalation, uniform voice, reverent to convention, epilogues, quiet endings. GPT = gossip as plot device, distant retrospection, subverted expectations. Gemini = tidy endings, bleak settings. Kimi = the generic center, no distinctive choices.

## Source 3: Desaire, Chua, Isom, Jarosova, Hua — "ChatGPT or academic scientist?" (Univ. of Kansas, 2023)

Twenty hand-built features + XGBoost separated Science "Perspectives" articles from ChatGPT essays at 94% per paragraph and **99.5–100% per document** — 20× fewer errors than the RoBERTa-based GPT-2 Output Detector on the same data. The features, by what they mark:

*Human markers*: more sentences and words per paragraph; higher stddev of sentence length; bigger length jumps between consecutive sentences; sentences under 11 words; sentences over 34 words; presence of ( ) ; : ? and dashes; the words **"but", "however", "although", "because", "this"**; numbers; capitals (proper nouns/acronyms) more than 2× the count of periods; "et" (citations).

*ChatGPT markers*: single quotes; the words **"others" and "researchers"** — citing ambiguous groups where humans name the specific scientist.

Buried in the discussion, the single best stat in the whole literature: **the standard deviation of paragraph length (in words) alone classifies documents at AUC 0.98.** More predictive on its own than the deep-learning detector.

What this validates or changes for the skill: "however" and "but" are *human* words, never to be banned (moreover/furthermore remain slop); the long-sentence bar belongs at ~30+, not 23; paragraph variance must be measured in words; vague crowd attribution is a bannable tell; parens/colons/question marks are human punctuation.

## Source 4: Akinwande, Adeliyi, Yussuph — "Decoding AI and Human Authorship" (IJCI, 2024)

500K-essay Kaggle corpus (Human ~63%, AI ~37%), Random Forest at 91% accuracy, AUC 0.96. The headline: **average word length was the top feature at 0.466 importance — three times the second-place feature.** AI ≈ 4.97 chars/word; human ≈ 4.39. Humans wrote longer essays (421 vs 343 words avg) with more unique words per essay (174 vs 157); AI wrote longer *words*. Both corpora lean mildly positive in sentiment, humans slightly more so. Also notable: a fine-tuned BERT hit only 63% on the same data — the countable surface features beat the black box.

Skill translation: the "short words" rule and the nominalization check. The half-character gap is Latinate abstraction, and it survives phrase-level de-slopping completely.

## Source 5: Georgiou — "What Distinguishes AI-Generated from Human Writing?" (BDCC, 2026)

PRISMA rapid review of 40 empirical studies. Organizes all known discriminators into five cue families: surface (lexical/stylometric — most pervasive and most consistently operationalized), discourse/pragmatic (stance, metadiscourse, rhetorical moves — AI approximates the genre template but distributes stance differently), epistemic/content (grounding, experience-without-experience), predictability/probabilistic (detector scores — powerful but fragile), and provenance (watermarks).

The finding that matters for this skill: **no single cue is stable across genres, and surface cues are the easiest to strip by paraphrasing** — detection only holds up when *layered* cue families are checked together. That is the argument for the lint script checking phrases AND rhythm AND lexicon AND structure simultaneously, and for never treating a clean phrase-scan as a pass. Also documents detector bias against non-native English writers (surface "cleanliness" is not proof of AI) and that fluent AI text coexists with measurable cue differences.

## Source 6: Khedr & Abbas — "AI in Literary and Non-Literary Discourse" (AWEJ, 2026)

Systematic review of 35 studies across creative and informative writing. Recurring results:

- **Homogenization**: AI fiction forms "tightly uniform clusters" stylometrically (O'Sullivan 2025); 11,800 GPT-4o-mini stories from 236 country prompts collapsed into the same nostalgic small-town harmony narrative (Rettberg & Wigers 2025). AI's *range* across pieces is as detectable as any single piece.
- **Affect flattening**: LLM-generated persuasion rated "more logical, better informed, and less angry" than human messages; human messages "more unique" with "more vivid storytelling" (Bai et al. 2025). Humans have a wider emotional range, including irritation — supports the commit-to-opinions rule, including negative opinions.
- **Flawed heuristics** (Jakesch et al. 2023, PNAS, 4,600 participants): readers judge contractions, first-person, and family references as "human" — cues AI can trivially produce ("more human than human"). Reader intuition is not a defense; measurable structure is.
- Durak et al. 2025: human texts had more diverse vocabulary and longer sentences; AI sentences "noticeably more predictable."

Skill translation: when producing multiple pieces in a session, vary the skeleton between them (two posts sharing an opening shape is a corpus-level tell); don't sand anger or irritation out of a piece that has it.

## Source 7: O'Sullivan — "Stylometric comparisons of human versus AI-generated creative writing" (HSSC, 2025)

Burrows' Delta over the 100 most frequent words (function words — content-independent) on the Beguš story corpus (250 human, 210 LLM). Humans form broad, heterogeneous clusters; GPT-3.5, GPT-4, and Llama 70b each form tight clusters, grouped inside a broader "AI" region. **GPT-4 clusters tighter than GPT-3.5** — refinement increases uniformity, and uniformity is the fingerprint. Occasional GPT-3.5/human overlaps exist but are rare. Direct answer given: can LLMs write creative prose statistically indistinguishable from humans? "No, at least, not yet." Also an explicit ethics caveat: stylometric deviation is unsuited to accusing individuals (people vary across time, task, fatigue, language background).

Skill translation: the "Don't wear the same disguise twice" section and the linter's multi-file house-style audit. The human signature is dispersion — a rulebook executed identically every time recreates the tight cluster it was meant to escape.

## Source 8: Terčon & Dobrovoljc — "Linguistic Characteristics of AI-Generated Text: A Survey" (2026, 44 studies)

The consolidation. Findings split cleanly into two piles:

*Consistent across studies*: lower lexical diversity (especially of function words) and smaller vocabulary; more repetition (words, expressions, high-order n-grams, POS sequences); more nouns/determiners/adpositions and nominalization, fewer adjectives/adverbs → formal, impersonal register; fewer proper nouns and first-person pronouns; fewer sensing verbs (read, look, hear), feeling words, and idioms; no aggressive or rude expressions; discourse markers fewer *and* more repetitive; fewer epistemic/modal markers; less varied punctuation (commas+periods dominate); rigid SVO constituent order; more neutral sentiment; less "involvement" (Biber) in every genre tested.

*No consensus / flips by genre, model, or baseline*: average word length, average sentence length, syntactic complexity direction, named entities, sentiment polarity, emotional content (AI hotel reviews **more** emotional than human ones; AI news **less** angry/fearful). Sardinha: abstractness differences only appear once genre is controlled — AI academic text has *more* persuasion than human academic text, AI essays *less* than human essays. Model fingerprints diverge (GPT-4o overuses downtoners and avoids clausal coordination; Llama 3 does the opposite; Qwen2.5 measured closest to human). And the detection-killer: prompting an LLM to *rephrase existing human text* defeats feature-based classifiers.

Skill translation: cues in the "consistent" pile can be defaults everywhere; cues in the "flips" pile must be register dials, not laws. This is the empirical basis for the Situate-first section and `--register`.

## Source 9: Etaat — "Exploring linguistic fingerprints in human and AI-generated texts" (Ampersand, 2026)

The reference-population paper. 80 intermediate L2 learner essays vs 80 GPT-4 essays on identical prompts, with GPT-4 *explicitly instructed to write at intermediate level* — and it still couldn't hide: higher lexical diversity (MTLD 111 vs 77), longer sentences (13.8 vs 10.1 words), deeper syntax trees, worse readability (grade 6.2 vs 3.9), 4× fewer surface errors. Every one of those directions is the *opposite* of the Desaire scientist study — because the human baseline moved, not the AI. Direction-stable human markers: opinion markers ("I think": humans 54, AI 25), possibility markers, more pronouns and auxiliaries. Direction-reversed markers: "however" (AI 9, humans 0), "even though" (AI 20, humans 2), "because" (AI 60, humans 48) — the equivocal-connective rule from Desaire holds against *expert* humans but flips against learners. AI discourse-marker distributions were also more uniform across essays than the humans' (dispersion again).

Skill translation: "who is the human this text claims to be?" matters as much as "is this human?". The equivocal check stays as a floor (zero equivocation is robotic in any voice) but is explicitly not a quota. "I think" and plain readable sentences beat concessive sophistication as humanity signals in casual registers. Topic vocabulary was also the false-positive source in our register tests — hence the linter now excludes repeated topic words from word-length and nominalization stats.

## How the two map to non-fiction writing (the translation this skill makes)

Fiction findings → blog/email/caption rules:
- "Narrator states the theme" → moral endings, universal closers, "ultimately it's about" — banned.
- "Embodied emotion" → in short non-fiction, name the feeling plainly; don't perform it somatically.
- "No subplots / tidy chains" → allow one digression or aside; don't tie every sentence to the thesis; endings can stop early or stay open.
- "Vague allusions" → name the actual product, place, price, article, person.
- "Reader address" → occasional direct address and parentheticals are human signatures.
- "Temporal complexity" → open mid-story; don't narrate in strict setup→payoff order.
- "Rarity/diversity" → when a phrasing feels like the default first thing anyone would write, write the second or third thing instead.

## The scoring model (scripts/slop_check.py)

The lint script operationalizes ~30 checks from these findings into a weighted 0–100 score. Alignment target: ≥90. The script is calibrated so that known slop (the field guide's ukulele example) scores low and edited human prose scores high. Checks that don't apply to a format (e.g., paragraph variety in a 30-word caption) are excluded from the denominator rather than passed for free.

## The July 2026 stress test (why checks 25–29 exist)

Sources 3–6 were converted into 13 measurable variables and run against a corpus of skill-passing drafts (8 formats, all scoring 92.9–100 on the then-current checker) plus slop controls. The critical experiment: a "stealth slop" blog post written with zero banned phrases, contractions, specifics, and deliberately varied sentence lengths — but with AI structure intact (latinate vocabulary, no equivocation, a vague crowd citation, uniform paragraphs, wall-to-wall commas). **It scored 98.4/100 on the old checker while failing 5 of the paper-derived metrics** (avg word length 7.4 chars vs human ~4.4, zero but/because/although, "many professionals experience difficulties", no ? ( ; :, no 30+ word sentence). Exactly the paraphrase-evasion failure mode Source 5 predicts for surface-only detectors.

Five checks were added or hardened in response, calibrated on that corpus (post-fix: honest drafts 95–100, stealth slop 84.4, generic slop 42–77):

- **wordlen** (Source 4's top feature): avg chars/word on lowercase tokens ≤4.65, so proper nouns don't inflate it.
- **nominal**: -tion/-ity/-ment/-ance density ≤3.5 per 100 words (honest drafts measured 0–3.2; de-surfaced AI prose 18–20).
- **equivocal** (Source 3): at least one but/because/although/though/yet per 120+ words.
- **vaguegroups** (Source 3): "experts agree" / "many professionals" / "researchers say" / "individuals" flagged.
- **punctrange** (Source 3): 150+ words must use at least one of ? ( ; :.
- Hardened: long-sentence bar 23→30 words (full credit); paragraph variety now measured as word-count CV (the AUC-0.98 stat), weight raised.

## The second stress test (why the checker grew registers and a house-style audit)

Sources 7–9 predicted two failure modes in the skill itself, and both reproduced:

1. **House style.** An audit of eight skill-passing drafts across formats found the skill's own devices hardening into a skeleton: most pieces ended on a short punchy beat, several opened on a number detail, and the phrase "I tried to" appeared in two different deliverables. Each piece scored 95–100 alone; together they form exactly the tight cluster O'Sullivan describes. Response: the "Don't wear the same disguise twice" section, and multi-file mode in the linter (2+ files → cross-piece report of shared openers, enders, and repeated distinctive phrases).

2. **Register false positives.** A well-written human postmortem *failed* the checker (89.3) on contractions, word length, and nominalizations — all topic vocabulary ("certificate rotation", "authentication service"). A sincere condolence note was flagged for the lone beat "Truly." as one-word drama. Response: `--register formal` (relaxes contractions/word-length/nominalization thresholds and gives one free lone beat; hard bans unchanged); topic words (content words repeated 3+ times) excluded from word-length and nominalization stats in every register; a lone one-word sentence now costs little while stacks still zero the check; signoffs no longer count as fragment-stack beats. Post-fix: postmortem 94.5 under formal, condolence 99.1 casual / 100 formal, all original samples 95–100, all slop controls still fail (42–84), stealth slop fails even under formal (84.0).

The design principle both fixes share, and the reason the skill is now organized as bans-plus-dials: the few phrase-level tells with no legitimate use in any register stay absolute; every distribution-level cue is conditioned on the situation, because the research says its direction is too.
