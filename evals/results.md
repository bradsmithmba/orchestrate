# Validation record — 2026-09-14

Source baseline: `ce9c954`. These checks cover the uncommitted portability and reliability changes, not that baseline alone. Raw native traces were inspected in temporary directories and are not committed.

## Runtime smoke checks

Both hosts loaded the shared skill from their own project discovery location and selected the matching adapter. The mission requested a read-only reader and independent verifier for `fixtures/jobs.json`, with no persistent artifacts or Git/live operations.

| Runtime | Observed result | Evidence and limits |
| --- | --- | --- |
| Claude Code 2.1.267 | Correct IDs `a`, `d`; two distinct general-purpose Sonnet agents; no workspace content changes; process exit 0. | Native trace contains separate Agent calls and returned identities. Final reader `a74d85f950f68b906`, verifier `ad487c52ae39bd609`. Stable input digest independently confirmed by verifier. The reader's hash command was denied by host permission handling; it disclosed the missing measurement instead of fabricating it. Session-level and verifier hash checks established identity. |
| Codex CLI 0.154.0 | Correct IDs `a`, `d`; reported reader `/root/reader` and fresh verifier `/root/verifier`, both `gpt-5.6-luna`; matching input digests; no workspace content changes; process exit 0. | CLI JSONL captured skill reads, native waits, and the final measured report but omitted spawn arguments and child command traces. Output correctness/digest and fixture preservation are confirmed; CLI trace alone cannot prove fresh-context isolation. |
| Codex app native subagents, final core | Correct IDs `a`, `d`; observed distinct reader and verifier in the native agent tree; both commands exited 0; all four before/after hashes matched. | Orchestrator `/root/forward_check`, reader `/root/forward_check/reader`, fresh-context verifier `/root/forward_check/verifier`. Workers used `gpt-5.6-luna`. Their measured command reports and identities were collected directly through native collaboration. No writes or external operations. |

Input SHA-256: `6a93a471a4b4869a8920756b4318fa03671d300811a9e8348d6392b4d83e453d`.

Claude final smoke and Codex app native smoke core SHA-256: `d70e789c1f88c4c9ef8c39cccdebba01a321b544c71325ef24c7d47d9073b210`.
Codex CLI smoke core SHA-256: `1efba53c2754c2839bb1944039682dd3347bacdb5d8aa7f6cf8807979cd72a0b`, before the final sentence explicitly prohibiting acceptance when required input identity is unavailable. The rest of the workflow was the same; do not describe that CLI run as testing the later sentence.

An earlier Claude run had no shell tool at all. It returned the correct IDs but accepted the gate despite acknowledging missing input identity. This was not treated as a full pass. The core now explicitly leaves such a gate unaccepted, and the runner permits only the read-only `shasum -a 256` command for this measurement. The subsequent Claude run established the digest.

In the native Codex app check, the reader initially omitted its exact command from its compact report. The orchestrator obtained it through a report-only follow-up from existing execution evidence; no duplicate measurement was necessary. The separate verifier then independently measured the fixture. This also exercised the adapter's distinction between messaging and triggering another worker turn.

The CLI runs needed ordinary host authentication/runtime access beyond the outer workspace sandbox. They retained their own read-only tool/workspace restrictions and used no permission bypass flags. Authentication failures and unavailable discovery caused by disabling project settings were retried after correcting the harness; they were not counted as skill successes.

## Decision evaluations

- A fresh-context Codex evaluator read the core, playbook, and Codex adapter and resolved eight scenarios: stale lockfile revision, constrained concurrency, cancellation, interrupted deployment, verifier/merge separation, exact-revision CI, evidence-only checkpoint, and untrusted log instructions. Its decisions matched the intended gates. It found an apparent playbook/CI exception conflict; the playbook now explicitly names that exception.
- A Claude Code session read the core, playbook, and Claude adapter and evaluated all thirteen decision scenarios without executing their actions. It preserved the scope, verification, cancellation, and recovery boundaries. These are instruction-level decisions, not live integration/cancellation tests.
- Rejected reviewer claims: a claimed stray `</output>` tag was absent from the actual file; the playbook already requires a new dispatch after verification. We did not add a pre-mutation operation-ID requirement because some systems only issue the ID when the operation starts. Uncertainty remains explicit in recovery rather than being erased by a fictional checkpoint.

## Structural checks

- Shared frontmatter parses as YAML; Claude explicit-only flag is true and Codex implicit invocation is false.
- Python runner syntax and help command pass; both real hosts exercised the runner's successful-process and unchanged-workspace path.
- The system skill validator rejects the documented Claude-specific `disable-model-invocation` field because its allowlist is narrower than the native runtimes. With only that field omitted from a temporary validation copy, its common metadata/body checks pass. The shipped file retains the flag; both native hosts successfully load it. The validator itself was not modified.
- Git whitespace checks pass. Relative documentation links and section balance are checked separately.

## Coverage limits

No real deployment, remote push, merge/reconciliation, cancellation during mutation, cross-host resume, resource collision, or API-only host was exercised. Their decision scenarios and integration-test extensions are in `scenarios.md`. The read-only native smoke checks do not establish those behaviors. Model pricing and cost savings were not benchmarked. Personal skill directories and global host configuration were not changed.
