# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-07-08

### Added
- `docs/templates/` — output templates for four archetype artifacts (SPIKE_FINDINGS, UNSHIP_LIST, EXPERIMENT, HEALTHCHECK).
- README section "When not to use each archetype" — per-archetype anti-patterns with the correct alternative dispatch.
- `CONTRIBUTING.md` and this `CHANGELOG.md`.
- `docs/evals/` — five manual boundary-behavior eval scenarios, one per code archetype, plus a pass/fail rubric.
- Hardened CI: agent-name uniqueness, tool-allowlist policy, boundary-marker presence, marketplace path resolution, and eval-scenario structure checks (`.github/scripts/validate_agents.py`).
- `version` fields (1.1.0) on both plugins in `.claude-plugin/marketplace.json`.

### Changed
- Seven agent files gained a one-line pointer to their output template (all except `code-agents/builder.md`).

## [1.0.0] - 2026-07-07

Initial release, versioned retroactively as shipped.

### Added
- Five Claude Code subagents: Prototyper, Builder, Sweeper, Grower, Maintainer.
- Three knowledge-work counterparts: Prototyper, Sweeper, Grower.
- `scripts/spike.py` and `scripts/churn_report.py`.
- Plugin marketplace with `code-archetypes` and `knowledge-archetypes`.

[1.1.0]: https://github.com/mfreidlitz/claude-agent-archetypes/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/mfreidlitz/claude-agent-archetypes/releases/tag/v1.0.0
