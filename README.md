# no-slop

A Claude Code skill that writes prose the way people actually write, not the way AI defaults to.

Most "sound more human" prompting only fixes surface tics — banning "delve" and em-dash overuse. That's not enough. A 2026 study of 61,608 stories found AI writing detectable at 93% accuracy from *structural* choices alone, even after the surface style was edited to pass; another separated ChatGPT from working scientists at 99%+ using twenty countable features, and a 500K-essay classifier ranked plain average word length as the strongest tell of all. This skill targets both layers: word-level habits (latinate inflation, filler verbs, hedging, tidy transitions) and structural ones (over-explained themes, uniform sentence and paragraph rhythm, missing equivocation, showing-not-telling emotion, missing specificity).

Use it for anything meant to be read by a person: blog posts, newsletters, LinkedIn/X posts, emails, cold outreach, cover letters, bios, About pages, product descriptions, announcements.

## Before / after

**LinkedIn post**

❌ Before:
> In today's fast-paced digital world, businesses are constantly looking for ways to streamline their operations. That's why I'm excited to announce that we've launched our new invoicing tool. It's not just about sending invoices — it's about giving business owners back their time. Whether you're a freelancer or a growing agency, this tool empowers you to get paid faster and focus on what matters most. The best part? Setup takes less than five minutes. Let's face it, nobody got into business to chase down payments!

✅ After:
> I built this because I was manually chasing down four late invoices last March, at 11pm, from my phone. The tool sends the reminder for you, three days before and three days after the due date. Setup is one CSV upload. If you freelance and you're still doing this by hand, it's free through June.

The before has a vapid opener, a "not just X, it's Y" scaffold, a fake question pivot, a rule-of-three ("freelancer or agency," "get paid faster... focus on..."), and a closer that states a moral. The after opens mid-scene, names one real detail (11pm, March, a phone), and ends on a plan instead of a lesson.

**Cold outreach email**

❌ Before:
> Dear Maria, I hope this message finds you well! I'm a passionate web developer dedicated to helping small businesses elevate their online presence. I noticed your website could benefit from a redesign, and I'd love to hop on a quick 15-minute call to discuss how we can work together to unlock your site's full potential.

✅ After:
> Hi Maria, your menu page took about 8 seconds to load on my phone (tested on 4G this morning). That's usually enough for people to give up and check Google Maps instead. I rebuild sites for small food businesses; did a bakery's shop page last year. Want me to send a 2-minute video of what I'd fix first? Alex

The before is generic enough to send to any business on earth ("elevate," "unlock," "full potential") and asks for a call before earning one. The after leads with a specific, checkable observation, states the credential as one line with proof, and asks a small question instead of a calendar slot.

**Product description**

❌ Before:
> Nestled in the heart of Delhi, our vibrant store boasts a myriad of rare plants, carefully curated to bring joy and tranquility into your home. Whether you're a seasoned plant parent or just starting your journey, we have something for everyone.

✅ After:
> The shop's in Shahpur Jat, down the lane past the cafe. Right now there are about 40 species on the shelves, mostly aroids and a few variegated monstera we don't usually get in stock.

The before is scene-setting filler ("nestled," "vibrant," "boasts," "myriad," "journey") that says nothing a reader can check. The after gives a location, a count, and a specific detail a customer could walk in and verify.

Run any draft through the linter to see this scored directly:

```bash
python3 scripts/slop_check.py before.md --format social
python3 scripts/slop_check.py after.md --format social
```

The "before" examples above score well under the 90 pass bar; the "after" versions clear it.

## What's in here

- [`SKILL.md`](SKILL.md) — the skill definition: before-you-draft checklist, voice rules, and format-specific guidance.
- [`references/patterns.md`](references/patterns.md) — the catalogue of AI-writing tells this skill avoids.
- [`references/formats.md`](references/formats.md) — per-format guidance (blog, social, email, cover letter, generic).
- [`references/research-notes.md`](references/research-notes.md) — the empirical studies this skill is built on.
- [`scripts/slop_check.py`](scripts/slop_check.py) — a standalone linter that scores a draft 0–100 against the same checks, stdlib-only, no dependencies.

## Installing

Copy the contents of this repo into your Claude Code skills directory:

```bash
git clone https://github.com/<your-username>/no-slop.git ~/.claude/skills/no-slop
```

Claude Code will pick it up automatically. Invoke it directly with `/no-slop`, or just ask Claude to write something human-facing — the skill's description is written to trigger on its own.

## Using the linter standalone

```bash
python3 scripts/slop_check.py draft.md --format blog
python3 scripts/slop_check.py report.md --format generic --register formal
python3 scripts/slop_check.py a.md b.md c.md   # adds a cross-piece house-style audit
```

Add `--json` for machine-readable output. A score of 90+ is the passing bar; anything lower prints the exact line and check that failed. `--register formal` relaxes the checks whose research evidence is genre-conditional (contractions, word length, nominalizations) for reports, postmortems, and serious notes — hard bans stay hard. Passing several files audits them as a set for shared openers, enders, and repeated phrases, because uniform habits across pieces are their own AI tell.

## Status

Validated at 99.6% pass rate on Claude Sonnet 5 across the test formats in `references/`.
