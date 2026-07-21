<worker_brief_template>
Every worker brief carries these sections, in this order, whether the worker's role is recon, build, merge, deploy, or closeout: the Scope section is where role differs (recon: read-only, no commits, no writes; merge: reconciliation against the updated mainline and sequencing; deploy: live-system safety limits and the rollback path; closeout: status docs, registries, and the final regression backstop), not a separate template. Omit a section only when it genuinely does not apply. On small single-track missions, Hard style rules, Reporting integrity, and If blocked stay mandatory in full; the remaining sections may be condensed to a sentence each.

### Identity and workspace
- Who the worker is (track, stage), the exact workspace path (worktree or primary checkout), the branch, the expected starting HEAD, and "work ONLY there".
- "Do NOT spawn subagents; execute yourself through to completion; run commands blocking/foreground; never idle waiting for notifications."

### Hard style rules
- The project's zero-exception rules, restated verbatim in every brief (they decay if assumed). Gather these from the project's own style guide or the user's stated preferences at mission start; this template does not hardcode them. Example shape from one project: no em dashes, no emojis, never a specific figurative term the user has banned, in any file or commit message.
- Credential hygiene, every brief: never place credentials or secret values in brief text, reports, commit messages, or committed files; pass them via environment variables at execution time only; run the project's secrets scan before every push where one exists.

### Reporting integrity
- "Your final report is independently verified by re-running your commands. Quote ONLY exact measured output." Include the current true baselines so the worker can self-check, and name any prior misreporting incident as a warning.

### Authority order
- The project's document precedence, top wins, including any recent additions a stale worker would miss.

### Rulings
- Any orchestrator rulings this stage must honor, stated as binding, with instruction to record them in the worker's artifacts (plan doc, ADR addendum, ops doc).

### Scope
- The stage's deliverables, with the governing planning doc named as authoritative over the brief's own summary. State what is explicitly OUT of scope and where the boundary is recorded.

### Known pitfalls
- The current ledger entries relevant to this stage (see pitfall_ledger below).

### Process
- Plan doc first, then incremental deliverable commits with the project's commit-prefix convention and trailer. Push after the plan, after each major deliverable, and at final green. NEVER force-push. Note any parallel track whose shared-file edits the worker must ignore (the orchestrator sequences merges).

### Tests and gates
- Tier-by-tier expectations with exact expected counts where known; sibling regression baselines; quality gates (lint, format, types, audit, secrets) run to fully Passed; safety limits for anything touching live systems, restating the mission's blast radius in concrete terms (which environments, which paths, which database, which rows, what is forbidden).

### If blocked
- The stop conditions: authority contradiction, expected-vs-found mismatch, two failed fix attempts, blast-radius pressure. "STOP and report precisely rather than improvising."

### Final message spec
- An explicit lettered list of what the report must contain: deliverables with commit shas, exact measured output lines per suite, gate results, build-time decisions with rationale, deviations, and concerns for the next stage.
</worker_brief_template>

<verification_brief_template>
Verification workers analyze and report; they change nothing in the repo and follow this shape:

- Identity and workspace: which worker's claim is being checked, the exact workspace path (a fresh checkout or worktree at the claimed commit, not a reused build-worker checkout), and the branch.
- "Do NOT spawn subagents; execute yourself through to completion; run commands blocking/foreground; never idle waiting for notifications."
- Hard rules travel with the verifier too: restate the project's zero-exception style rules and the credential-hygiene rule verbatim in every verification brief.
- Restate the mission's blast radius in concrete terms; the verifier's commands must not mutate anything beyond it, and any state its checks create (containers, temp rows) is cleaned up and confirmed clean.
- State the build worker's claims as a checklist with expected numbers.
- Re-run every claimed suite; quote exact summary lines; diff against claims.
- For claimed data changes: run the equivalent read query against the affected rows/tables and diff the actual state against the claim. For claimed deployments: check the live service's status endpoint, logs, or version marker directly rather than trusting the deploy command's exit code. For claimed merges or reconciliations: verify the merge-base and diff the shared files against mainline to confirm the change is confined to what was claimed.
- Spot-check the riskiest paths by reading code with file:line citations: write boundaries (no writes outside the module's own schema or directory), safety guards on live-system tests, the specific logic the build worker itself flagged as fragile, and the shared-file diff against the mainline (must be confined to the expected files).
- Audit for leaked credentials: scan the build worker's diff and commit messages for secret values, and confirm the project's secrets scan ran where one exists.
- For live-system checks: pre-read the test to confirm it only touches self-created state BEFORE running it; verify zero orphaned rows after; never apply migrations or fix infrastructure unless the brief explicitly authorizes it, report instead.
- "Flag any discrepancy loudly." A verifier that finds the tree healthy but the report wrong should say exactly that.
- If blocked: authority contradiction, expected-vs-found mismatch, or blast-radius pressure. STOP and report precisely rather than improvising a fix; verifiers apply no fixes beyond what their brief explicitly authorizes.
- Final message spec: an explicit lettered list of what the report must contain: the claims checklist with pass/fail per item, exact measured output lines per suite, the discrepancies found (if any), and any spot-checked file:line citations.
</verification_brief_template>

<observed_failure_modes>
Worker failure modes seen repeatedly in production use, and the response that works:

- **Stale-count echo**: worker reports documented baseline numbers instead of measured output; tree is healthy, report is wrong. Response: verification catches it; correct the audit trail; keep the reporting-integrity clause loud in every brief.
- **Idle-on-watch**: worker starts a blocking or background watch, then ends its turn "waiting for the notification". Response: orchestrator checks real state, takes over the watch if useful, resumes the worker with precise next steps and "do not pause for notifications".
- **Self-delegation**: worker reports it "launched a background agent" instead of working. Response: immediate resume with a direct order to execute personally; forbid subagents in every brief.
- **Premature stop as "blocked"**: worker halts on scope size rather than a genuine blocker, delivering a plan instead of the work. Response: resume with a numbered execution order and per-step commit instructions; remind it that commit-per-step makes context exhaustion safe.
- **Directive-vs-authority conflict**: worker correctly identifies that an orchestrator directive contradicts project authority docs and implements the compliant alternative. Response: accept, credit it, record the correction. The authority order outranks the orchestrator's brief by design.
- **External interference**: stray stop-work or kill signals not from the user or orchestrator. Response: halt affected work, verify with the user, then resume from the committed checkpoint; instruct workers to accept work-control only from the orchestrator.
- **Discrepancy stop done right**: worker halts on an expected-vs-found mismatch that turns out to be a stale expectation in the brief itself. Response: resolve by arithmetic or measurement, rule, resume. The stop was correct behavior; never train it out.
</observed_failure_modes>

<pitfall_ledger>
Maintain a per-project ledger of traps already paid for once. Propagate relevant entries into every brief. The entries below are worked examples from a Python/SQLAlchemy project, kept to show the level of specificity a ledger entry needs, not a portable starter set: replace them with your own stack's traps.

- Alembic's relative `script_location` resolves against CWD, not the ini file: run migrations from the module root; pin `script_location` absolutely in every test-constructed AlembicConfig.
- detect-secrets flags its own baseline file: exclude the baseline from its own scan.
- Marker-based pytest selection silently skips unmarked tests while directory-based selection runs them: every test carries its tier marker; marker mode is the canonical count.
- `uv sync` bare installs only the root package: workspace test runs need `--all-packages --dev`; CI's isolated `--locked --package X --extra dev` sync exposes test-time dependencies that full syncs mask, so declare them explicitly in the dev extra.
- Alembic revision ids longer than 32 characters overflow the default `alembic_version` column.
- Live-service guards must check BOTH the credential/DSN naming convention AND the host, never either alone.
- CI runners are slower and smaller than dev machines: CPU-heavy integration tiers that run in minutes locally can take hours on shared runners; scope CI tiers deliberately.
</pitfall_ledger>
