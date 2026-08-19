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
/plugin install exfu-agent-library-solo@exfu
```

Refresh the catalogue later with `/plugin marketplace update exfu`.

## Plugins

| Plugin | What it is | Source repo |
| --- | --- | --- |
| `exfu-agent-library-solo` | ExFu Agent Library — solo edition for individuals | [ExFu/agent-library](https://github.com/ExFu/agent-library) → `plugins/solo` |
| `exfu-agent-library-team` | ExFu Agent Library — joiner edition for team members | [ExFu/agent-library](https://github.com/ExFu/agent-library) → `plugins/team` |
| `exfu-agent-library-team-admin` | ExFu Agent Library — library-champion edition | [ExFu/agent-library](https://github.com/ExFu/agent-library) → `plugins/team-admin` |
| `exfu-agent-planning-and-delegating` | ExFu planning methodology + grounded multi-model delegation (Codex via clink) | [ExFu/agent-planning-and-delegating](https://github.com/ExFu/agent-planning-and-delegating) → `plugins/exfu-agent-planning-and-delegating` |
| `exfu-humane-agents` | Humane agent conventions — dual-audience reporting first | [ExFu/humane-agents](https://github.com/ExFu/humane-agents) → `plugins/exfu-humane-agents` |
| `exfu-agent-plan-visualiser` | Event-sourced planning: git-history extraction and projections | [ExFu/agent-plan-visualiser](https://github.com/ExFu/agent-plan-visualiser) → `agent-plan-visualiser` |

## How it works

The catalogue lives in [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json).
Each plugin lives in a subdirectory of its own repo, so each entry uses a
[`git-subdir`](https://code.claude.com/docs/en/plugin-marketplaces#git-subdirectories)
source — Claude Code sparsely clones only that subdirectory when a user installs
the plugin.

No source pins a `ref` or `sha`, so each entry tracks its repo's default branch.
The catalogue therefore needs no edit when a plugin changes — only when the set
of plugins, their names, or their subdirectory paths change.

### Versions live in the source plugin, not here

Entries here deliberately carry no `version` field. Claude Code resolves a
plugin's version from the first of: `plugin.json` → the marketplace entry → the
git commit SHA, and it uses the `plugin.json` value
[without warning](https://code.claude.com/docs/en/plugin-marketplaces#version-resolution-and-release-channels)
when both are set. A `version` here would be inert, and would silently drift
from the real one.

To publish an update: bump `version` in the source plugin's `plugin.json` and
push. Users pick it up on their next `/plugin marketplace update` (or the
background auto-update) followed by `/plugin update`.

**If you push a plugin change without bumping its `plugin.json` version, nobody
receives it.** Claude Code sees an unchanged version and keeps the cached copy
indefinitely.

### Maintaining an entry

When you add, rename, or remove a plugin:

1. Edit `.claude-plugin/marketplace.json`.
2. Keep `name` and `source.path` in sync with the source repo.
3. Commit and push — users pick up changes on their next `/plugin marketplace update`.

To rename or remove a plugin without breaking existing installs, add a top-level
[`renames`](https://code.claude.com/docs/en/plugin-marketplaces#rename-or-remove-a-plugin)
map (requires Claude Code v2.1.193+).
