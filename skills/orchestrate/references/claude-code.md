# Claude Code adapter

Read this only in Claude Code. Tool parameters vary with host version and configuration; use the callable schema rather than assuming every example below is available.

## Workers and lifecycle

- Spawn a general-purpose worker with the Agent tool. Prefer background execution for independent work when supported. If the host chooses foreground execution, preserve stage gates and run sequentially.
- Keep the returned agent identity. Use the host's result/status tools or completion notifications to collect its report. SendMessage can steer or resume workers where its live schema permits; verify whether the recipient is running and whether another turn actually started. If it cannot resume, create a replacement from the durable checkpoint.
- Use native stop controls on authenticated cancellation. Preserve the last known checkpoint and mark interrupted work unverified.
- Workers must not spawn children, even if the installed runtime allows it. Do not accidentally launch an agent team when a subagent was intended; inspect the call's semantics.

## Models and context

- The orchestrator remains the session model. Worker and verifier defaults are `sonnet`, overridden by the mission's explicit preference or an applicable configured role. Validate availability through the host's exposed model options or a launch result. Report unavailable choices; never retry indefinitely.
- Use a fresh, non-fork worker for verification with only the brief, claim checklist, applicable project rules, and evidence references. A separate identity with the build conversation copied into it does not meet the fresh-context requirement.

## Filesystem and state

- Use explicit worktree isolation when supported by the actual spawn call. Confirm the worker's path, branch, and HEAD in its first report; do not infer isolation from its agent name or background status.
- If automatic isolation is unavailable, delegate worktree setup to a bounded setup worker, then assign absolute paths to writers. Native Git worktrees are the fallback; no external agent service is needed.
- Mirror mission status in native task tools when available. The mission record described in PLAYBOOK.md remains the recovery source; native tasks and memory do not replace it.

## Discovery

Install the complete skill directory at `.claude/skills/orchestrate/` or `~/.claude/skills/orchestrate/`. A symlink to the canonical directory is supported for local installations. Invoke `/orchestrate`; `disable-model-invocation: true` in SKILL.md enforces explicit invocation. Keep this orchestration skill in the main session, without `context: fork`.

References, checked 2026-09-14: [skills](https://code.claude.com/docs/en/skills), [subagents](https://code.claude.com/docs/en/subagents).
