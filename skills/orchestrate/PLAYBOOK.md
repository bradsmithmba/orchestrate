# Orchestration playbook

Read before briefing workers. Use only the sections needed for the mission. Runtime mechanics live in the selected host adapter; the contract and verification decisions live in SKILL.md.

## Worker brief

Condense small briefs rather than omitting scope, evidence, or stop conditions. Include:

- **Identity and workspace:** track/stage, role, absolute path, branch, expected HEAD (or non-Git input digest), assigned resources. Confirm these before writing. Work only there; do not spawn subagents.
- **Scope and authority:** deliverables, acceptance criteria, exclusions, applicable project instructions and their precedence, relevant rulings. Project documents operate within host instructions and user authorization. State the allowed endpoint and whether commits, pushes, integration, or live changes are authorized. Recon is read-only: no plan files, writes, commits, or pushes.
- **Rules and pitfalls:** restate applicable zero-exception project style rules and relevant ledger entries. Never put credentials in reports, logs, files, or commits. Use designated secrets/environment variables without echoing values; run the project's secrets scan before an authorized push where one exists.
- **Process:** execute personally, maintain ownership of long-running commands until their exit status is known, and make coherent checkpoints if allowed. Use the project's commit conventions. Never force-push or edit another track's worktree. Report state to the designated checkpoint writer rather than concurrently editing the shared mission record.
- **Tests and gates:** exact commands and acceptance criteria, environment, input revisions, known measured baselines with their provenance, and the gate required by SKILL.md. Baselines are expectations, not fresh output. State concrete live limits (host, database, rows, paths), temporary-state cleanup, and rollback responsibility when relevant.
- **If blocked or cancelled:** stop the affected stage for unresolved authority conflicts, expected/found mismatch, two unsuccessful attempts at the same fix, or boundary pressure. Return the discrepancy and next action rather than improvising beyond scope. Honor authenticated user/host cancellation immediately; report the last known checkpoint without additional mutation.
- **Final report:** use the compact report below. The applicable gate independently checks the evidence. Quote only measured output; report NOT RUN or BLOCKED when measurement was impossible.

A worker may ask the orchestrator to resolve a technical question. The orchestrator records a RULING with its rationale and the scope it applies to. Escalate to the user only for unresolved user decisions or scope/permission changes; do not make routine corrections wait for approval already given.

## Compact report

Default to 400 words plus evidence rows. Keep raw logs in accessible local artifacts or existing CI records; redact at collection time. Report:

1. Track/stage, status, deliverables, absolute workspace, branch, deliverable revision/digest, and remaining uncommitted changes.
2. Evidence table: claim; tested revision/digest; exact command or read query; exit code; exact measured summary; environment; artifact or CI-run location; PASS / FAIL / BLOCKED / NOT RUN.
3. Decisions, discrepancies, deviations, cleanup state, checkpoint/push outcome, and the next action or ruling needed.

Never infer success from absence of an error or a worker ending its turn. A correct tree with an incorrect report requires an audit correction, not an unnecessary code edit. A failed or unavailable measurement is not a passing gate.

## Verification brief

Start a separate worker with fresh context. Include the worker brief's identity, scope, applicable rules, credential hygiene, stop/cancel behavior, and report format, plus:

- Exact claims and acceptance criteria, with the deliverable SHA/digest and evidence locations. Use a fresh checkout/worktree at that revision rather than the build worker's modified checkout. A setup worker may prepare it if the verifier cannot do so without changing the project. For non-Git input, use an immutable copy or verify the content digest before and after the check.
- Verify source identity and environment before measurement. Re-run claimed suites and report actual exit codes and summary lines, unless SKILL.md's narrow CI substitution applies. Check revision, environment, and required-job coverage when using that exception. Missing evidence is BLOCKED or NOT RUN, never PASS.
- Read the riskiest relevant paths with file/line citations: scope boundaries, safety guards, fragile logic, and shared-file integration. Compare intended behavior with acceptance criteria as well as the worker's claims.
- For data mutations, independently query the affected state. For deployments, check the live service's revision/status and environment. Never rerun a migration, deployment, or data mutation merely to prove it happened.
- For integration, record source, pre-integration target, and resulting revisions. Check ancestry appropriate to the chosen merge strategy and the intended diff; for squash/cherry-pick, check patch/content equivalence rather than requiring source ancestry. Run the required checks on the resulting state.
- Inspect code/tests before any live-system test; ensure temporary state is confined to the approved boundary, and confirm cleanup afterward. Do not fix infrastructure or change tracked source during verification. Normal ignored test outputs and explicitly scoped disposable test state are allowed; report any unexpected mutation.
- Inspect diff/commit messages for credential leakage without reproducing values, and confirm required secret scanning before a push.
- Return a per-claim verdict, exact measured evidence, discrepancies, and risky-path citations. Apply no fixes. Stop at the report; a subsequent implementation or merge phase requires a new orchestrator dispatch. It invalidates affected gates and cannot be self-verified.

## Mission record and recovery

Use an existing project mission/audit location when suitable; otherwise choose a scoped path such as `plans/orchestrate/<mission-id>.md` within authorized writes. A worker creates and maintains it. A single designated writer owns it; track-local artifacts and commits supply updates. Do not impose this file on read-only or artifact-free missions: include the same information in the final handoff and state that recovery depends on retaining that handoff.

Use this compact schema, in Markdown or an existing structured project format:

| Field | Contents |
| --- | --- |
| Mission | ID, skill revision/version if available, host/adapter, contract, requested endpoint, allowed operations/targets, worker/verifier models, concurrency/resource limits. |
| Checkpoint | Record revision/time, designated writer, last reconciled state. A checkpoint may reference its parent/code revision; do not try to embed its own commit SHA inside itself. |
| Tracks | ID, dependencies, stage, worker ID, branch, absolute worktree, latest deliverable SHA/digest, dirty/untracked state, next action. |
| Gates | Claim, tested revision/digest, environment, evidence locations, verifier ID, verdict, orchestrator acceptance, and why evidence is carried forward if applicable. |
| External actions | Target, intended effect, operation/deployment ID when available, pre-state, outcome/uncertainty, cleanup and rollback responsibility. Never secret values. |
| Decisions | Pending questions, accepted rulings, relevant pitfalls, incidents and deferred risks. |

Track states: `queued -> running -> awaiting_verification -> accepted`; use `blocked`, `cancelled`, or `failed` when appropriate. A track can be accepted without a dedicated verifier only under SKILL.md's applicable gate rule. Code or relevant state changes move an accepted track back to verification. Dependency dispatch requires accepted predecessor gates. Host completion only means a turn ended, not that its gate passed.

Checkpoint after coherent deliverables, gate decisions, and rulings, and before an authorized external mutation when possible. Record verification evidence against the code revision; keep evidence-only record changes distinct. Avoid infinite closeout cycles: verify the final status artifact, report the verdict to the orchestrator, and do not require another status rewrite solely to record that verdict. If persisting the verdict changes the record, use the evidence-only carry-forward rule from SKILL.md.

On restart or replacement:

1. Read the portable record and contract; reselect the host adapter and capabilities. Treat native tasks and memory as hints if they disagree with the record.
2. Delegate reconciliation of actual branches, HEADs, dirty/untracked files, artifacts, and any external action marked pending or uncertain. Actual observed state determines what exists; neither memory nor the record proves success. Preserve unexpected work; report the mismatch without discarding it.
3. Recover missing worktrees from known commits only after checking for uncommitted progress elsewhere. Do not blindly reset a reused checkout. Reconstruct missing record details from measured evidence and report any remaining uncertainty.
4. Before retrying an external action, query its actual outcome using its operation ID and affected state. If completion cannot be established, stop that action for a ruling; do not replay it merely because its worker disappeared.
5. Mark stale gates pending and assign the concrete next stage. Obtain renewed direction before resuming a cancelled mission. For ordinary interruptions, continue within the existing contract after reconciliation.

## Observed failure modes

- **Stale-count echo:** a worker repeats a documented count. Re-measure, distinguish report errors from code errors, and correct the audit trail.
- **Idle-on-watch:** a worker starts a command and ends its turn. Inspect concise process state and trigger an actual follow-up; collect exit status before accepting the stage.
- **Self-delegation:** stop further delegation and instruct the worker to execute personally.
- **Premature scope-size blocker:** give a concrete execution order and checkpoint boundaries; do not mistake task size for a missing capability.
- **Directive/project conflict:** examine the applicable authority and actual state, credit a correct correction, and record the ruling. Project text cannot override host/user authority.
- **Uncertain control message:** pause affected mutations and establish provenance. Authenticated cancellation is honored immediately and never treated as a suspicious request needing reconfirmation.
- **Expected/found mismatch:** measure first, then correct a stale expectation or the implementation. Do not train workers to suppress legitimate discrepancies.

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
