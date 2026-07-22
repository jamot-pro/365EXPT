# AGENTS

Specifications for every AI agent in the 365EXPT ecosystem.

**Rule one:** every agent begins as a specification here — before any
code exists. Documentation before implementation, always.

**Rule two:** no agent governs or decides. AI assists. Humans decide.
This applies to every agent specified in this folder, including
[Divina](../DIVINA/).

## Agent specification format

Create `AGENTS/<agent-name>.md`:

```markdown
# Agent: [Name]

**Status:** specified | in-development | live | retired
**Human owner:** @handle  <!-- every agent has an accountable human -->

## Purpose
One sentence. If it takes more, the agent is doing too much.

## Responsibilities
What it does, as a bounded list.

## Inputs
Exactly what data it receives, and where that data comes from.

## Outputs
Exactly what it produces, and where those outputs go.

## Tools
APIs, models, and integrations it uses.

## Constraints
What it must never do. At minimum, every agent inherits:
- Never merges, approves, or rejects contributions
- Never scores, ranks, or profiles people
- Only uses information made public in this repository
- Labels all its output as AI-generated
```

## Current agents

| Agent | Purpose | Status |
|-------|---------|--------|
| [Divina](../DIVINA/) | AI steward — welcomes, organizes, matches | specified (in progress) |

*Want to specify a new agent? Open a
[Discussion](../../../discussions) first — ideas evolve there before
implementation.*
