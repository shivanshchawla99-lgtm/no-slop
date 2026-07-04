# Research Notes

Where the rules come from. Two sources, analyzed July 2026.

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

The lint script operationalizes ~26 checks from these findings into a weighted 0–100 score. Alignment target: ≥90. The script is calibrated so that known slop (the field guide's ukulele example) scores low and edited human prose scores high. Checks that don't apply to a format (e.g., paragraph variety in a 30-word caption) are excluded from the denominator rather than passed for free.
