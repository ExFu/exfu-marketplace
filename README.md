# exfu-marketplace

A single [Claude Code plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces)
that makes every ExFu-owned plugin installable from one place. The plugins
themselves live in their own repositories; this repo is just the catalogue that
points at them.

## Add the marketplace

```
/plugin marketplace add ExFu/claude-marketplace
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
| `exfu-agent-plan-visualiser` | Event-sourced planning: git-history extraction and projections | [ExFu/agent-plan-visualiser](https://github.com/ExFu/agent-plan-visualiser) → `agent-plan-visualiser` |

## How it works

The catalogue lives in [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json).
Each plugin lives in a subdirectory of its own repo, so each entry uses a
[`git-subdir`](https://code.claude.com/docs/en/plugin-marketplaces#git-subdirectories)
source — Claude Code sparsely clones only that subdirectory when a user installs
the plugin.

Versions are pinned to each plugin's `plugin.json`. To publish updates: bump the
version in the source plugin, push it to its repo, and (optionally) update the
matching `version` here so the catalogue stays accurate.

### Maintaining an entry

When you add, rename, or remove a plugin:

1. Edit `.claude-plugin/marketplace.json`.
2. Keep `name`, `version`, and the `source.path` in sync with the source repo.
3. Commit and push — users pick up changes on their next `/plugin marketplace update`.

To rename or remove a plugin without breaking existing installs, add a top-level
[`renames`](https://code.claude.com/docs/en/plugin-marketplaces#rename-or-remove-a-plugin)
map (requires Claude Code v2.1.193+).
