# Contributing to 365EXPT

Everyone can contribute. Most contributions need no code.
If you have five minutes, read [START-HERE.md](START-HERE.md) first.

---

## Non-technical contributions

These matter just as much as code — often more:

- **Submit a real problem** — [Problem issue](../../issues/new?template=problem.md).
  Real problems are the fuel of the whole experiment.
- **Improve documentation** — anything unclear, fix it. PRs welcome on
  every `.md` file.
- **Research** — investigate existing solutions to a listed problem and
  comment your findings on its issue.
- **Interview** — talk to someone whose work is changing because of AI
  and publish the write-up in [DISCOVERIES/](DISCOVERIES/).
- **Translate** — bring any document to another language.
- **Ask good questions** — in [Discussions](../../discussions).
  Curiosity over certainty.

## Technical contributions

- **Improve Divina** — her prompt, memory design, capabilities, and
  architecture live in [DIVINA/](DIVINA/). Specification first, then
  implementation.
- **Specify or build an agent** — every agent starts as a spec in
  [AGENTS/](AGENTS/) (responsibilities, inputs, outputs, tools,
  constraints).
- **Build an integration** — Telegram, Discord, WhatsApp, GitHub, MCP,
  A2A. Start with a spec in [INTEGRATIONS/](INTEGRATIONS/).
- **Run an experiment** — see "Experiment workflow" below.

## The rules of the road

1. **Markdown-first. Specification-driven.** Documentation before
   implementation. Every feature begins with a specification. If your
   PR adds behavior with no spec, expect to be asked for the spec first.
2. **Every experiment is documented.** Problem, hypothesis, method,
   results, lessons, next steps — using the
   [experiment template](EXPERIMENTS/TEMPLATE.md).
3. **Every decision is explainable.** If you can't explain why, write
   it down as an open question instead.
4. **Failures are contributions.** A documented failure in
   [DISCOVERIES/](DISCOVERIES/) is more valuable than an undocumented
   success.
5. **AI assists. Humans decide.** Use AI tools freely to help you
   contribute — and say so when you do. A human is accountable for
   every merged change.
6. **People come before technology.** Consent before publishing
   anyone's problem or words. Kindness before cleverness. See
   [BLUEPRINT/](BLUEPRINT/) for community rules.

## Experiment workflow

1. Propose it: open an
   [Experiment issue](../../issues/new?template=experiment.md) or a
   Discussion.
2. Once it's real, create `EXPERIMENTS/<short-name>/` from
   [EXPERIMENTS/TEMPLATE.md](EXPERIMENTS/TEMPLATE.md).
3. Run it. Update the folder as you go — not just at the end.
4. Publish what you learned in the experiment folder, and promote the
   key lesson to [DISCOVERIES/](DISCOVERIES/).
5. If the experiment outgrows the lab and becomes a venture, document
   the journey in [VENTURES/](VENTURES/).

## Issues and labels

Use the templates when they fit. Labels you'll see:

`good-first-issue` · `research` · `documentation` · `design` ·
`community` · `agent` · `integration` · `bug` · `experiment` ·
`help wanted`

If you're new, filter by
[`good-first-issue`](../../issues?q=is%3Aissue+is%3Aopen+label%3Agood-first-issue).

## Pull requests

- Small and focused beats large and sprawling.
- Explain the *why* in the description, not just the *what*.
- Documentation-only PRs can be done entirely in the GitHub web editor.
- Every contributor gets a genuine, human response. That's a promise
  the community makes and keeps.

## Recognition

Contributors are credited in the experiments and discoveries they touch.
There is no scoring or ranking system — recognition here means your
name on real work, in public, permanently.
