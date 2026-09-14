# Codex adapter

Read this only in Codex. Tools differ across app, CLI, and hosted sessions. Use the available schemas and host instructions; the names below are mappings, not requirements to call nonexistent tools.

## Workers and lifecycle

- Use delegated subagents for mission work. Do not create user-owned app tasks as a substitute for subagents unless the user explicitly asks for those tasks.
- When the host exposes `collaboration`: use `spawn_agent` to start work, `list_agents` for state, `send_message` to steer a running worker, `followup_task` to trigger work in an idle worker, `wait_agent` for notifications, and `interrupt_agent` to stop it. A message alone does not start an idle worker's next turn.
- Other Codex runtimes may expose `spawn_agent`, `send_input`, `wait`, `resume_agent`, and `close_agent`. Match the operation to the actual schema; retain returned identifiers and distinguish a completed turn from an agent that cannot be resumed.
- Respect the session's concurrency limit, including whether the parent consumes a slot. Queue work when full; collect completed results and release slots using the host's lifecycle controls when available. Do not repeatedly spawn into a full pool.
- Use bounded native waits and process continuations so progress remains observable. A yielded command or a worker's commentary is not evidence of successful completion.

## Models and context

- The orchestrator remains the session model. Respect explicit mission model/effort choices, then applicable configured worker/verifier choices. Otherwise choose a supported worker model intended for economical execution from the session's available model descriptions. Record the choice; do not assume a fixed GPT model name or equate lower reasoning effort with a cheaper model.
- If the host exposes only inheritance, use it only when it satisfies the mission's model requirements, and disclose that a cheaper tier is not established. If economical execution is a hard requirement, resolve that capability before dispatch.
- Where `fork_turns` exists, use `"none"` with a self-contained brief for verifiers. In hosts where a full-history fork fixes model/effort to the parent, use the supported fresh-context path to select a worker model. Otherwise use the host's documented independent-context mode. Do not silently replace a fresh verifier with a conversation fork.
- Workers must not delegate further, even when their tools allow it.

## Filesystem and state

- Do not assume spawning isolates the filesystem. Some Codex sessions share one working directory across all subagents. Delegate explicit Git worktree setup when necessary; assign absolute paths and require each worker to confirm path, branch, and HEAD before writing.
- When a shell tool supports a working-directory argument, set it on every command. A prior `cd` is not a durable assignment. Respect host sandbox permissions for the worktree and Git metadata.
- Native task/progress tools are optional mirrors. Keep the portable mission record authoritative; do not create recurring app automations to wait for ordinary workers.

## Discovery

Install the complete directory at `.agents/skills/orchestrate/` or `~/.agents/skills/orchestrate/`. Local Codex discovery supports symlinked skill directories. Invoke `$orchestrate` in CLI/IDE or select the skill in the app. `agents/openai.yaml` disables implicit invocation; the Claude frontmatter flag is not the Codex invocation control.

References, checked 2026-09-14: [skills](https://learn.chatgpt.com/docs/build-skills), [subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents). Live session schemas remain authoritative for operation names and capabilities.
