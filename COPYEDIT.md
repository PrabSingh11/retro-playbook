# Copyedit process

How to proofread this book and recommend changes -- run this whenever chapter prose
needs a pass, or before publishing a batch of new/edited chapters. It's a **recommend
changes** process, not a silent-rewrite one: the book's ideas and anything needing
Prab's sign-off stay out of scope.

## 1. Run the structural check (mechanical, safe to auto-fix)

```bash
python3 scripts/copyedit_check.py            # everything in chapters/
python3 scripts/copyedit_check.py chapters/03-facilitation-101.html   # one file
```

Catches: unbalanced HTML tags (`div`/`section`/`article`/`aside`/`ul`/`ol`/`li`), citation
links (`references.html#some-id`) that don't resolve to a real `id=` in
`references.html`, orphan reference entries nothing cites, and dead internal links.
Fix anything it reports directly -- these are mechanical, low-risk, reversible via git.

## 2. Read for voice (judgment call, report + suggest, don't silently rewrite style)

Derived from the book's existing chapters and Prab's standing direction (2026-07-20):
**keep it fun and easy to read -- if a change makes it feel more like a textbook, it's
the wrong change.**

On-voice:
- Direct address, contractions, short punchy sentences mixed with longer ones.
- Concrete and specific over abstract ("Dave won't stop talking", not "certain
  participants may dominate discussion").
- **What to do** / **Try this line** labels stay terse and imperative.
- Em dashes, italics for asides, second person ("you") are all normal -- not errors.

Off-voice, worth flagging:
- Corporate throat-clearing ("In today's fast-paced environment...", "It is important
  to note that...").
- Hedging ("might potentially", "could possibly").
- Passive constructions where an active one reads better.
- Generic listicle phrasing that could belong to any retro-format article on the internet.

For each hit, quote the line, say why it's off-voice, and suggest a rewrite -- but leave
the actual call to whoever applies the pass, since tone is subjective.

## 3. Typos and grammar (mechanical, safe to auto-fix)

Standard proofreading: spelling, subject-verb agreement, dangling modifiers, doubled
words. Fix directly.

## 4. Fabrication check (non-negotiable, see backlog history)

If a chapter states something as fact -- a statistic, a study finding, a named
real-world example -- with no `class="cite"` link next to it, flag it. This book has
been caught out on fabricated claims before, so:
- **Never** invent a citation to make a flagged claim look sourced.
- Either verify the claim (WebSearch) and add a proper citation following the existing
  `references.html` pattern (id + claim + source + note, linked via
  `<a href="../references.html#id" class="cite">`), or
- Rephrase it as an explicit opinion/heuristic ("in practice, teams tend to..."), or
- Drop it.

## 5. Design-system reuse

New markup should reuse existing classes from `assets/book.css` (`.recipe`, `.card`,
`.promptcard`, `.pinned`, `.cheat`, `.flow`, `.script`, `.diagram`, etc.) instead of
introducing one-off inline styles or a new class for something an existing one already
covers.

## Output

A report grouped by file:

```
chapters/03-facilitation-101.html:42 -- [typo] "recieve" -> "receive"
chapters/09-remote-and-async-formats.html:88 -- [voice] "It is important to note that
    timeboxing can be beneficial" reads like a textbook -- try "Timeboxing works.
    Here's how." or similar direct phrasing.
chapters/04-the-icebreaker-box.html:60 -- [fabrication] "studies show 80% of teams..."
    has no citation -- verify, rephrase as opinion, or drop
```

End with a one-line count per category (typos / voice / citations / design-system /
fabrication). Apply the mechanical fixes (step 1, step 3, unambiguous parts of step 4);
leave voice and content calls as recommendations for review.
