# Contributing

This repo is one implementation of Boris Cherny's five archetypes. It stays deliberately minimal. Contributions are welcome where they sharpen the discipline of an existing archetype or the verifiability of the package; they are declined where they add coordination, configuration surface, or scope the design principles rule out.

## What makes a good agent change

A good change makes an archetype's boundary sharper or its shown-output discipline stronger without adding coordination. Concretely: it keeps the agent self-contained per task (no cross-agent state), it preserves "the human keeps the judgment, the agent keeps the discipline," and it keeps verification by shown output rather than the agent's own attestation. Prose beats configuration; a clearer boundary sentence is worth more than a new field.

## When tool allowlists may widen

Tool allowlists in each agent's frontmatter are deliberately minimal per archetype (see the README customization note). Widen them consciously, never by default, and never in a way that erases an archetype's boundary: the knowledge-work Prototyper and Grower get no `Edit` or `Write` because they propose rather than modify — that is boundary, not oversight. A widening is justified only when the archetype's own discipline still holds with the new tool present. CI enforces the current policy (see below); a deliberate policy change updates both the frontmatter and the check in the same commit.

## How new archetype proposals are judged

New archetypes are anchored in Cherny's five. The bar for an addition is "an energy with no home" — a task energy that none of the existing five carries and that your existing function agents cannot host. Proposals that duplicate an existing energy, or that exist to hold the other agents together, are declined by the no-coordinator principle. A proposal must show the energy, the tasks it serves, and why no current archetype or main-session workflow already covers it.

## What counts as a breaking change

A breaking change alters a published contract that installs or dispatches depend on: an agent `name`, an agent's frontmatter contract (the `name`/`tools`/`description` fields consumers rely on), or the plugin structure (`marketplace.json` plugin names, the `agents` arrays, the `.plugin` layout). Breaking changes bump the major version and are called out in the CHANGELOG. Prose edits, boundary tightening, and new templates are not breaking.

## Workflow and orchestration tooling is out of scope

This repo ships archetype agents, not an orchestrator. Loop drivers, handoff state, dispatch routers, and meta-reporting are out of scope by the no-coordinator principle: each agent is self-contained per task, and orchestration stays with the main session or the human. First-party Claude Code features (hooks, `/loop`, `/goal`) already cover the mechanical parts. If a loop framework is ever wanted, it is a separate repo with its own contract.

## Releasing

Version fields live in `.claude-plugin/marketplace.json` (one per plugin). The Cowork release artifact `knowledge-archetypes.plugin` is a zip of the knowledge plugin: its manifest, its agents, and the shared templates. Build it from the repo root with:

    powershell -Command "Compress-Archive -Path .claude-plugin/marketplace.json, knowledge-agents, docs/templates -DestinationPath knowledge-archetypes.zip -Force; Move-Item knowledge-archetypes.zip knowledge-archetypes.plugin -Force"

Then attach `knowledge-archetypes.plugin` to the GitHub release. Tag `v1.0.0` on the initial commit and `v1.1.0` on the release commit; push tags; create the release. The `code-archetypes` plugin installs from the marketplace and needs no separate artifact.
