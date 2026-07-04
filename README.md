# no-slop

A Claude Code skill that writes prose the way people actually write, not the way AI defaults to.

Most "sound more human" prompting only fixes surface tics — banning "delve" and em-dash overuse. That's not enough. A 2026 study of 61,608 stories found AI writing detectable at 93% accuracy from *structural* choices alone, even after the surface style was edited to pass. This skill targets both layers: word-level habits (filler verbs, hedging, tidy transitions) and structural ones (over-explained themes, uniform sentence rhythm, showing-not-telling emotion, missing specificity).

Use it for anything meant to be read by a person: blog posts, newsletters, LinkedIn/X posts, emails, cold outreach, cover letters, bios, About pages, product descriptions, announcements.

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
```

Add `--json` for machine-readable output. A score of 90+ is the passing bar; anything lower prints the exact line and check that failed.

## Status

Validated at 99.6% pass rate on Claude Sonnet 5 across the test formats in `references/`.
