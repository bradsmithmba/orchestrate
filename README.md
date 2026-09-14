# orchestrate

A single skill for Claude Code and Codex that separates orchestration, execution, and independent verification.

The session model plans, briefs workers, reviews evidence, and resolves questions. Workers perform file work in assigned workspaces. Independent verifiers check claims before dependent stages proceed. This keeps bulky file contents and logs out of the orchestrator's context; actual cost depends on model selection, repeated checks, and coordination overhead.

## How it works

- **Shared workflow, host-specific mechanics.** One core defines scope, gates, cancellation, and recovery. The selected adapter maps worker lifecycle and model choices to available tools.
- **Scope comes from the request.** A report, local artifact, review branch, merge, or deployment can be the endpoint. Commits, pushes, integration, and live actions follow existing authorization.
- **Workers execute personally.** Concurrent writers use separate branches/worktrees. Shared runtime resources are assigned or serialized. The orchestrator delegates setup and checkpoint writes too.
- **Evidence belongs to a revision.** Fresh-context verifiers independently check the claimed state. Later edits or integration invalidate affected gates. A narrow existing-CI exception avoids redundant test reruns.
- **Recovery is portable.** One mission record tracks revisions, gates, pending actions, and rulings. Native tasks and memory are optional mirrors. A fresh host reconciles actual state before resuming.

## Structure

```text
skills/orchestrate/
  SKILL.md                    Shared rules, capability check, mission contract
  PLAYBOOK.md                 Briefs, reports, recovery, pitfall ledger
  references/claude-code.md    Claude Code lifecycle, models, isolation
  references/codex.md          Codex lifecycle, models, isolation
  agents/openai.yaml          Codex explicit-invocation policy
evals/
  run_smoke.py                 Disposable read-only native-runtime check
  scenarios.md                Behavioral cases and review rubric
  results.md                  Recorded validation and limitations
  fixtures/jobs.json          Smoke-test input
```

## Installation

Keep `skills/orchestrate/` as the canonical source. Copy the **entire directory** to the appropriate location, or use local directory symlinks so both hosts read the same files:

| Scope | Claude Code | Codex |
| --- | --- | --- |
| Personal | `~/.claude/skills/orchestrate/` | `~/.agents/skills/orchestrate/` |
| Project | `.claude/skills/orchestrate/` | `.agents/skills/orchestrate/` |

For example, from this repository's root on macOS/Linux:

```sh
mkdir -p ~/.claude/skills ~/.agents/skills
ln -s "$PWD/skills/orchestrate" ~/.claude/skills/orchestrate
ln -s "$PWD/skills/orchestrate" ~/.agents/skills/orchestrate
```

These commands do not replace an existing installation. Inspect an existing destination before updating it. Avoid duplicate copies at multiple discovery locations. Local symlinks do not package the skill for remote hosts; copy the complete directory into that host's supported location. No plugin or global model-setting change is required.

## Usage and models

Invoke `/orchestrate` in Claude Code, `$orchestrate` in Codex CLI/IDE, or select the skill in the Codex app. Claude's `disable-model-invocation` and Codex's `agents/openai.yaml` policy enforce explicit invocation. Discussing or editing the skill does not invoke its mission workflow.

After invoking the skill, give the outcome and constraints, for example:

> Implement the approved parser changes on a local review branch. Commits are allowed; do not push or merge. Run the parser regression suite and have a separate worker verify the result.

The orchestrator stays on the session model. Explicit mission model choices take precedence over configured host preferences, then adapter defaults. Claude workers/verifiers default to Sonnet. Codex selects an available economical worker model from live host options; it does not hardcode a GPT release. The mission records actual choices and limitations. With inheritance only, the skill reports that a cheaper tier has not been established.

The initial targets are Claude Code and Codex environments with delegated workers and filesystem access. The skill checks actual capabilities rather than branding. Limited concurrency permits sequential execution. Missing workers or independent verification cannot be replaced by the orchestrator doing and checking its own work.

## Validation

Run with existing host authentication:

```sh
python3 evals/run_smoke.py --host claude
python3 evals/run_smoke.py --host codex
```

Each command consumes model usage, copies the skill into a disposable directory, requests a reader and fresh verifier, and records a trace. It does not install into personal directories or modify global configuration. Evaluation tools/workspace access are read-only; authentication and runtime caches may still need ordinary host access. No permission bypass flags are used.

A successful runner exit means the process completed without a detected error or workspace change; it does **not** prove correct delegation or verification. Review the trace using [the rubric](evals/scenarios.md). Run the shared failure scenarios on both hosts after behavioral changes. See [recorded results](evals/results.md) for actual coverage.

## License

MIT
