# orchestrate

A Claude Code skill that turns the session model into a pure orchestrator: it thinks, decomposes, briefs, and gates, while background worker subagents do every file-level task and report back with measured evidence.

## What it does

`/orchestrate` runs multi-stage builds as a managed pipeline instead of a single long-running session:

- **Orchestrator does zero file work.** No edits, no writes, no test runs as deliverables. It plans, dispatches, reviews gates, and rules on disputes.
- **Workers execute in the background**, on their own branch and worktree, committing and pushing after every coherent deliverable so a killed or context-exhausted worker never loses progress.
- **Independent verification gates** re-run any worker's claimed tests or deployments before the pipeline advances, catching stale or misreported results rather than trusting them.
- **A foot-gun ledger** carries known tool and environment traps forward into every worker brief so the same mistake is never paid for twice.
- **Escalation is bounded.** The orchestrator resolves technical and scope questions autonomously within an agreed blast radius, and only surfaces genuine scope changes, destructive actions, or infrastructure decisions to the user.

## Why

Long, single-session agent runs tend to drift: context gets consumed by file edits and test output, verification gets skipped under time pressure, and a killed session loses unsaved state. Splitting the work into an orchestrator that never touches files and workers that checkpoint constantly fixes both problems: the orchestrator's context stays cheap, and progress survives worker failure.

## Structure

```
skills/orchestrate/
  SKILL.md       Core rules: role definition, pipeline, verification gates, escalation policy, definition of done
  PLAYBOOK.md    Worker and verification brief templates, observed failure modes, the foot-gun ledger
```

## Installation

Copy `skills/orchestrate/` into your Claude Code skills directory (`~/.claude/skills/orchestrate/` for a user-level install, or `.claude/skills/orchestrate/` inside a project for a project-level install).

## Usage

Invoke explicitly with `/orchestrate` or by naming the skill. It is deliberately scoped not to trigger on general mentions of subagents or parallel work, only on an explicit call, so it never hijacks a normal session.

Once running, the orchestrator asks a handful of high-leverage questions up front (done bar, safety limits, live-service bindings, budget posture) before dispatching any work.

## License

MIT
