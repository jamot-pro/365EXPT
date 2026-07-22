# INTEGRATIONS

Connections between 365EXPT and the places where people already are.
The community shouldn't have to come to the tool — the tool comes to
the community.

## Planned surface area

| Integration | Purpose | Status |
|-------------|---------|--------|
| **GitHub** | The home: issues, PRs, Discussions — already live by definition | live |
| **Telegram** | Community conversation, Divina access | not started |
| **Discord** | Community conversation, student communities | not started |
| **WhatsApp** | Reaching problem-owners where they already are | not started |
| **MCP** | Model Context Protocol server exposing problems/experiments to AI tools | not started |
| **A2A** | Agent-to-agent interoperability | not started |

## How to build one (Mission 6)

1. **Spec first.** Create `INTEGRATIONS/<name>/SPEC.md` describing:
   - Purpose — what community need it serves (not what tech it uses)
   - Data flow — exactly what crosses the boundary, in both directions
   - Privacy — what it never transmits; consent requirements
   - Human accountability — the @handle who owns it
2. **Discuss.** Open a [Discussion](../../../discussions) linking the
   spec.
3. **Build as an experiment.** The first deployment of any integration
   is an experiment in [EXPERIMENTS/](../EXPERIMENTS/) — with a
   hypothesis ("this integration will increase X") and published
   results, whatever they are.

## Constraints inherited by every integration

- No cross-platform tracking of individuals.
- Only public repository information flows outward by default;
  anything more requires explicit consent, specified in the SPEC.
- Every automated message is labeled as automated.
- An integration that stops serving the community gets retired — that's
  a discovery, not a failure.
