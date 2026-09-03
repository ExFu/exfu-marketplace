# exfu-marketplace

A single [Claude Code plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces)
that makes every ExFu-owned plugin installable from one place. The plugins
themselves live in their own repositories; this repo is just the catalogue that
points at them.

## Add the marketplace

```
/plugin marketplace add ExFu/exfu-marketplace
```

Then install any plugin by name:

```
/plugin install exfu-agent-library-solo@exfu-marketplace
```

Refresh the catalogue later with `/plugin marketplace update exfu-marketplace`, then
`/plugin update` to pick up new releases.

The marketplace is named `exfu-marketplace` everywhere: in this manifest, in the
CLI, and in the Claude Desktop app. Plugin IDs are always `<plugin>@exfu-marketplace`.

## Plugins

| Plugin | What it is | Source repo |
| --- | --- | --- |
| `exfu-agent-library-solo` | ExFu Agent Library — solo edition for individuals | [ExFu/agent-library](https://github.com/ExFu/agent-library) → `plugins/solo` |
| `exfu-agent-library-team` | ExFu Agent Library — joiner edition for team members | [ExFu/agent-library](https://github.com/ExFu/agent-library) → `plugins/team` |
| `exfu-agent-library-team-admin` | ExFu Agent Library — library-champion edition | [ExFu/agent-library](https://github.com/ExFu/agent-library) → `plugins/team-admin` |
| `exfu-agent-planning-and-delegating` | ExFu planning methodology + grounded multi-model delegation (Codex via clink) | [ExFu/agent-planning-and-delegating](https://github.com/ExFu/agent-planning-and-delegating) → `plugins/exfu-agent-planning-and-delegating` |
| `exfu-humane-agents` | Humane agent conventions — dual-audience reporting first | [ExFu/humane-agents](https://github.com/ExFu/humane-agents) → `plugins/exfu-humane-agents` |
| `exfu-agent-plan-visualiser` | Event-sourced planning: git-history extraction and projections | [ExFu/agent-plan-visualiser](https://github.com/ExFu/agent-plan-visualiser) → `plugins/agent-plan-visualiser` |

## How it works

The catalogue lives in [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json).
Each plugin lives in a subdirectory of its own repo, so each entry uses a
[`git-subdir`](https://code.claude.com/docs/en/plugin-marketplaces#git-subdirectories)
source — Claude Code sparsely clones only that subdirectory when a user installs
the plugin.

### Every entry is pinned to a commit

Each source carries a `sha`: the exact commit of the plugin repo that is
released. Installing gives you that commit, whenever you install. A plugin
repo's default branch is free to carry unreleased work; none of it reaches
users until this catalogue says so.

This is deliberate, and it is what makes updates reliable on both surfaces:

- **Claude Desktop** syncs marketplaces on Anthropic's servers and only
  re-reads the plugin repos when *this repo* has a new commit. Pushing to a
  plugin repo, or bumping its version, changes nothing until the pin here moves.
- **The CLI** caches plugins by their `plugin.json` version and keeps the cached
  copy while that version is unchanged.

So a release is exactly one thing: a commit here that moves a pin to a commit
whose `plugin.json` version is new. The release script enforces both halves.

### Releasing a plugin

```
scripts/release exfu-humane-agents            # pin the repo's current main
scripts/release exfu-humane-agents v0.2.0     # or a tag / branch / commit
```

The script resolves the commit, reads its `plugin.json`, refuses to proceed if
the version has not changed since the current pin, rewrites the entry, and
commits. Push the commit and users receive the release on their next refresh.

`scripts/check` runs the same validation CI does: manifest schema, every pinned
commit reachable, `plugin.json` name and version consistent with the entry, and
the structural rules Anthropic's server enforces silently (no top-level `bin/`,
no command/skill name collisions). `scripts/smoke-test` installs every plugin
into a throwaway home directory exactly as a new user would.

### Versions live in the source plugin, not here

Entries carry no `version` field. Claude Code reads `plugin.json` first and
uses it [without warning](https://code.claude.com/docs/en/plugin-marketplaces#version-resolution-and-release-channels)
even when the entry sets one, so a version here would be inert and would drift.
The pin is the field that is honoured.
