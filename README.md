# Claude Agent Archetypes

Boris Cherny's five product-engineering archetypes, implemented as ready-to-use Claude agents: five [Claude Code](https://docs.claude.com/en/docs/claude-code) subagents for software work, and three knowledge-work counterparts for non-engineering work. Plus two small scripts that turn the two most mechanism-shaped disciplines (throwaway spikes, evidence-based sweeping) into tooling instead of instructions.

## Background

In June 2026, Boris Cherny (creator of Claude Code) described the five archetypes he sees on a product engineering team ([original post](https://x.com/bcherny/status/2071379474277613732)):

1. **Prototyper** generates many new ideas; most never ship.
2. **Builder** turns a prototype or idea into production-grade product and infrastructure, fast.
3. **Sweeper** cleans up the UI, simplifies code and systems, unships, and optimizes performance.
4. **Grower** iterates on a built product to improve product-market fit.
5. **Maintainer** owns a mature system to keep it secure, reliable, fast, and efficient at scale.

Three clarifications from Cherny's own replies shaped this implementation:

- People (and agents) span 2-3 archetypes, and roles shift over time and across projects. So these agents are invoked per phase and per task, never assigned as fixed identities.
- A central coordinator works worse the faster ideas shift; people self-organize, and Claude can do some of that too. So there is deliberately no orchestrator archetype here.
- The archetypes are not specific to engineering. Hence the knowledge-work set.

He also noted the phase mix: pre-PMF work needs archetypes 1+2+3; growth with PMF needs 2+3+4 and a little 5; strong PMF needs 3+4+5 and a little 2. Use that as your dispatch guide.

## Design principles

**Archetypes are phase energies, orthogonal to function.** Your existing agents (a researcher, a writer, a reviewer) are functions. Archetypes describe what kind of energy a task needs: divergent overproduction, production-grade completion, subtraction, data-driven iteration, or stewardship. The same function can carry different energies on different days. Build archetype agents only where an energy has no home in your existing setup; document the mapping where it does.

**The human keeps the judgment; the agent keeps the discipline.** The Sweeper proposes deletions with evidence but never deletes user-visible things without sign-off. The Grower pre-registers expected effects before shipping. The Prototyper's spikes are mechanically exempt from quality gates because they are mechanically guaranteed to be disposable. Verification is by shown output, never by the agent's own attestation.

**No coordinator.** Each agent is self-contained per task. Orchestration stays with your main session (or with you).

## When not to use each archetype

The phase mix above says which energies a stage needs. This says where each archetype is the wrong tool, and who to dispatch instead.

- **Prototyper** is not for changes you intend to keep. A spike is disposable by construction; if you want the result in production, that is Builder work behind a spec. Dispatch Builder, not Prototyper, once the question is already answered.
- **Builder** is not for open questions. If the approach is unproven or an architecture decision is unmade, building locks in a guess. Spike it with the Prototyper first, or surface the decision to the human; Builder starts when the spec is a contract.
- **Sweeper** is not for adding capability or redesigning. Its diff only ever shrinks the system. New behavior is Builder work; a different design is a spec decision for the human. Sweeper without a green verify suite to preserve is also premature.
- **Grower** is not for pre-instrumentation products or missing features. With no data, its only valid output is an instrumentation proposal, not tweaks; a genuine capability gap routes to the spec flow for Builder, not into a growth iteration.
- **Maintainer** is not for feature requests or growth work. Stewardship shrinks risk, not scope. Route new features to Builder, product iteration to Grower, and simplification passes to the Sweeper.

## What's in the box

```
code-agents/          Claude Code subagents (all five archetypes)
  prototyper.md       throwaway spikes in isolated worktrees, findings note as deliverable
  builder.md          spec-anchored production slices with full verify discipline
  sweeper.md          post-milestone simplification, unship-lists with evidence
  grower.md           experiment-sized iterations from real analytics data
  maintainer.md       cadence-driven audits, upgrades, and health checks
knowledge-agents/     knowledge-work counterparts (three archetypes; see below)
  prototyper.md       idea batches with kill tests: content angles, options, concepts
  sweeper.md          unship-lists for documents, rules, gates, and process noise
  grower.md           funnel/engagement analysis with smallest-testable-iteration output
scripts/
  spike.py            create/list/reap throwaway spike worktrees with a gate-exemption marker
  churn_report.py     git-history evidence (stale files, low-churn heavyweights) for the Sweeper
docs/templates/       output-artifact format templates (Prototyper, Sweeper, Grower, Maintainer)
docs/evals/           manual boundary-behavior scenarios, one per code archetype
```

### Why only three knowledge-work agents?

Builder and Maintainer are deliberately absent from the knowledge-work set. In a typical knowledge-work setup, Builder energy already lives in your main session and drafting workflow (turning a chosen idea into a finished deliverable is what your primary loop does), and Maintainer energy lives in your scheduled rhythms (recurring briefs, scans, reviews, memory consolidation). Adding agents there would duplicate what exists, and per the no-coordinator principle, layers that exist to "hold the others together" are a smell. If your setup lacks those homes, the code-agents versions translate readily.

## Installation

The repo doubles as a Claude Code plugin marketplace with two plugins: `code-archetypes` (all five software subagents) and `knowledge-archetypes` (the three knowledge-work agents). They are separate plugins because three archetype names exist in both sets.

### Claude Code

Install as a plugin (recommended):

```
/plugin marketplace add mfreidlitz/claude-agent-archetypes
/plugin install code-archetypes@claude-agent-archetypes
```

`code-archetypes` is the primary install for software work. Add `knowledge-archetypes` too if you dispatch non-code work (research, content, analysis) from Code:

```
/plugin install knowledge-archetypes@claude-agent-archetypes
```

Run `/agents` to confirm. Invoke the agents by describing the task ("spike whether the API supports X", "run a sweep pass on the module") or by explicit dispatch.

Alternatively, copy the files into a single repository for a per-project install without the plugin system:

```bash
mkdir -p .claude/agents
cp code-agents/*.md .claude/agents/
```

### Claude Cowork

`knowledge-archetypes` is the one you want in Cowork. The easiest path: download `knowledge-archetypes.plugin` from the [Releases page](https://github.com/mfreidlitz/claude-agent-archetypes/releases) and install it through Cowork's plugin management (Settings > Capabilities). Alternatively, use the three markdown files in `knowledge-agents/` directly as agent definitions in your own plugin. Adapt the context-loading instructions to point at your own project files.

The knowledge-work agents also work as pasted personas in any Claude conversation, no installation required.

### Scripts

Both scripts are dependency-free Python 3.8+ and live wherever you keep repo scripts:

```bash
# Prototyper: create an isolated throwaway worktree
python scripts/spike.py new payment-api-feasibility --question "Can provider X do refunds?"
python scripts/spike.py list
python scripts/spike.py reap --days 14        # remove old spikes (confirms first)

# Sweeper: git-history evidence for the unship-list
python scripts/churn_report.py --stale-months 6 --top 20
```

The `.spike` marker file that `spike.py` writes into each spike worktree is the integration point for verification hooks: a pre-commit or verify script can check for it and skip quality gates inside spikes, keeping the "throwaway means exempt" rule mechanical.

## Example output

What the scripts produce (output format is exact; file names and numbers below are illustrative):

```
$ python scripts/spike.py new payment-api-feasibility --question "Can provider X do refunds?"
Spike worktree ready: /work/myrepo-spikes/payment-api-feasibility  (branch spike/payment-api-feasibility)
Reminder: the deliverable is a findings note in docs/spikes/, not this code.

$ python scripts/spike.py list
payment-api-feasibility     3d  Can provider X do refunds?

$ python scripts/spike.py reap --days 14
reap candidate: payment-api-feasibility (17d old)
Remove these worktrees and their branches? [y/N] y
reaped: payment-api-feasibility
```

```
$ python scripts/churn_report.py --stale-months 6 --top 20

# Churn report (2026-07-07)

Tracked files analyzed: 214. Staleness threshold: 6 months.

## Stale files (untouched > 6 months)

| File | Lines | Commits | Days since last touch |
|---|---:|---:|---:|
| src/legacy/export_v1.py | 412 | 2 | 391 |
| src/utils/feature_flags.py | 88 | 1 | 240 |

## Low-churn heavyweights (most lines per commit)

| File | Lines | Commits | Lines/commit |
|---|---:|---:|---:|
| src/legacy/export_v1.py | 412 | 2 | 206 |
| src/api/handlers.py | 350 | 14 | 25 |

*Evidence, not verdicts: cross-check candidates against runtime usage before proposing removal.*
```

A typical Sweeper dispatch then reads the report, cross-checks the candidates (grep for imports, check logs), and returns an unship-list where every row carries its evidence.

## Customization

The agents ship stack-agnostic. Per project, tighten three things:

1. **The verify command.** Builder, Sweeper, and Maintainer all reference "the project's verify command"; point them at yours (a `verify.py`, `make check`, `npm run verify`, whatever gates your definition of done).
2. **The spec anchor.** Builder and Grower reference "the spec"; name your actual document (PRD, requirements doc, issue tracker) in the agent file or in your project's `CLAUDE.md`.
3. **Performance budgets.** Sweeper and Maintainer work best against explicit numbers. If you have none, their first useful output is proposing some.

Tool allowlists in each agent's frontmatter are deliberately minimal per archetype (the knowledge-work Prototyper and Grower, for instance, get no Edit access: they propose, they don't modify). Widen them consciously, not by default.

## Verification and contributing

The discipline each archetype promises is checkable, not just described:

- **Output templates** in `docs/templates/` fix the shape of each agent's deliverable (spike findings, unship-list, experiment, health check). Each agent file points at its template.
- **Eval scenarios** in `docs/evals/` are a manual protocol: one boundary-behavior scenario per code archetype, each testing that the agent refuses the out-of-bounds action and routes to the correct alternative. `docs/evals/README.md` has the pass/fail rubric.
- **CI** (`.github/scripts/validate_agents.py`) enforces the agent contracts on every push: unique names, tool-allowlist policy (the knowledge Prototyper and Grower stay Edit/Write-free), a boundary marker in each agent body, and that the marketplace paths resolve.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for what makes a good agent change, when tool allowlists may widen, how new archetype proposals are judged, and the release process. Changes are tracked in [`CHANGELOG.md`](CHANGELOG.md).

## License

MIT. The archetype definitions belong to Boris Cherny's original post; this repository is one implementation of them.
