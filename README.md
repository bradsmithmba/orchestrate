# orchestrate

A Claude Code skill that enforces a split of thinking, work and validation across multiple tiers.

A smarter (more expensive) model acts as a leader/orchestrator, then capable-but-less-expensive models (Sonnet by default) execute the work, then that work is independently verified.

The orchestrator never edits, writes, or runs tests. It thinks, decomposes the mission into staged tracks, briefs workers, reviews their reports as gates, and rules on disputes. Every token spent on file diffs, command output, and test logs is spent by a worker, not by the orchestrator. This keeps the expensive model's context reserved for the one thing it is actually being paid for: judgment. Cost and context usage scale with the cheap tier, not the expensive one, even as the mission grows in size.

## What it does

`/orchestrate` runs multi-stage builds as a managed pipeline instead of a single long-running session:

- **Orchestrator does zero file work.** No edits, no writes, no test runs as deliverables. It plans, dispatches, reviews gates, and rules on disputes, so its context window is never consumed by raw command output or diffs.
- **Workers execute in the background** on cheaper models, on their own branch and worktree, committing and pushing after every coherent deliverable so a killed or context-exhausted worker never loses progress.
- **Independent verification gates** re-run any worker's claimed tests or deployments before the pipeline advances, catching stale or misreported results rather than trusting them.
- **A pitfall ledger** carries known tool and environment traps forward into every worker brief so the same mistake is never paid for twice.
- **Escalation is bounded.** The orchestrator resolves technical and scope questions autonomously within an agreed blast radius, and only surfaces genuine scope changes, destructive actions, or infrastructure decisions to the user.

## Why

Running one expensive model through an entire long build wastes most of what makes it expensive: its context fills with file edits and test output that a cheaper model handles just as well, and its per-token cost applies to every line of that noise. Long single-model sessions also drift: verification gets skipped under time pressure, and a killed session loses unsaved state.

Splitting the work fixes both problems at once. The orchestrator's context stays reserved for planning and judgment calls, so it stays cheap and coherent even on missions that would blow out a single session's context window. Workers checkpoint constantly, so progress survives worker failure regardless of which tier hits a limit first.

## Structure

```
skills/orchestrate/
  SKILL.md       Core rules: role definition, pipeline, verification gates, escalation policy, definition of done
  PLAYBOOK.md    Worker and verification brief templates, observed failure modes, the pitfall ledger
```

## Models

The skill runs on whatever model your Claude Code session is on, no configuration needed for the orchestrator side. Workers default to Sonnet, dispatched via the Agent tool as `model: sonnet`, but this is adjustable, not fixed: the user can override the worker model per mission.

The original intent behind the split was Fable as the orchestrator's brain and Sonnet as the workers: Fable's judgment directing Sonnet's execution. The skill works with any orchestrator/worker model pairing; that pairing was simply the design target.

## Installation

Copy `skills/orchestrate/` into your Claude Code skills directory (`~/.claude/skills/orchestrate/` for a user-level install, or `.claude/skills/orchestrate/` inside a project for a project-level install).

## Usage

Invoke explicitly with `/orchestrate` or by naming the skill. It is deliberately scoped not to trigger on general mentions of subagents or parallel work, only on an explicit call, so it never hijacks a normal session.

Once running, the orchestrator asks a handful of high-leverage questions up front before dispatching any work.

## License

MIT
