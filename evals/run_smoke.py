#!/usr/bin/env python3
"""Run a bounded native-host trace; behavioral verdicts require trace review."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile


def snapshot(root):
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.rglob("*")
        if path.is_file()
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", choices=("claude", "codex"), required=True)
    parser.add_argument("--timeout", type=int, default=240)
    args = parser.parse_args()
    if args.timeout < 1:
        parser.error("--timeout must be positive")
    executable = shutil.which(args.host)
    if not executable:
        parser.error(f"{args.host} is not installed or not on PATH")

    repo = Path(__file__).resolve().parents[1]
    output = Path(tempfile.mkdtemp(prefix=f"orchestrate-{args.host}-"))
    workspace = output / "workspace"
    discovery = ".claude" if args.host == "claude" else ".agents"
    shutil.copytree(repo / "skills/orchestrate", workspace / discovery / "skills/orchestrate")
    shutil.copyfile(repo / "evals/fixtures/jobs.json", workspace / "jobs.json")
    invocation = "/orchestrate" if args.host == "claude" else "$orchestrate"
    prompt = f"""{invocation}
Run a small read-only mission in this directory. Delegate reading jobs.json to one
worker: report the IDs of enabled jobs with retries less than 2. Have a separate
fresh-context verifier independently read the file and check the answer. Report
the measured result and both worker identities. This mission ends at the report.
Do not edit files, commit, push, merge, deploy, install anything, access external
services, or create persistent mission artifacts. No runtime tests or CI are
required. Use native delegated subagents and supported model choices. Keep the
entire run bounded to this small check. Do not ask questions already answered here.
Use shasum -a 256 jobs.json to establish content identity when shell access is available.
"""
    (output / "prompt.txt").write_text(prompt)
    before = snapshot(workspace)
    if args.host == "claude":
        command = [executable, "-p", "--output-format", "stream-json", "--verbose",
                   "--no-session-persistence", "--setting-sources", "project",
                   "--strict-mcp-config", "--permission-mode", "dontAsk",
                   "--allowedTools", "Bash(shasum -a 256 *)", "--tools",
                   "Read,Glob,Grep,Bash,Agent,SendMessage,TaskOutput,TaskStop,TodoWrite"]
    else:
        command = [executable, "exec", "--ephemeral", "--ignore-user-config",
                   "--skip-git-repo-check", "--sandbox", "read-only", "--json", "-"]
    print(f"Trace directory: {output}", flush=True)
    timed_out = False
    with (output / "trace.jsonl").open("w") as stdout, (output / "stderr.txt").open("w") as stderr:
        process = subprocess.Popen(command, cwd=workspace, stdin=subprocess.PIPE,
                                   stdout=stdout, stderr=stderr, text=True,
                                   start_new_session=True)
        try:
            process.communicate(prompt, timeout=args.timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.communicate()

    after = snapshot(workspace)
    changed = sorted(key for key in before.keys() | after.keys()
                     if before.get(key) != after.get(key))
    host_error = False
    completed = False
    for line in (output / "trace.jsonl").read_text().splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "result":
            completed = True
            host_error |= bool(event.get("is_error"))
            host_error |= event.get("subtype") != "success"
        elif event.get("type") == "turn.completed":
            completed = True
        elif event.get("type") in ("error", "turn.failed"):
            host_error = True
    summary = {
        "host": args.host, "exit_code": process.returncode, "timed_out": timed_out,
        "completion_event": completed, "host_error": host_error,
        "changed_workspace_files": changed,
        "skill_sha256": before[f"{discovery}/skills/orchestrate/SKILL.md"],
        "behavioral_verdict": "UNREVIEWED: inspect trace using evals/scenarios.md",
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return int(bool(process.returncode or timed_out or host_error or changed or not completed))


if __name__ == "__main__":
    raise SystemExit(main())
