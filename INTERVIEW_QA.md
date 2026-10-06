# ai-cloudops-agent — interview questions and answers

[README](README.md) · [Project architecture](PROJECT_ARCHITECTURE.md)

Answers below use this repository’s files and implementation. They distinguish existing behavior from suggested extensions; source links let you verify each walkthrough.

## 1. What problem does ai-cloudops-agent address, and what can you demonstrate?

`POST /agent/run` reads the goal. An investigation calls three tools in order: list alerts, read logs, check the manifest. The tool list is `mcp/tools.json`.

I would demonstrate the linked implementation or examples and distinguish that evidence from any planned production features. Start with [`README.md`](README.md).

## 2. How is this repository organized?

- [`src/cloudops/main.py`](src/cloudops/main.py): Implementation or supporting configuration.
- [`src/cloudops/ops.py`](src/cloudops/ops.py): Implementation or supporting configuration.
- [`src/cloudops/agent.py`](src/cloudops/agent.py): Implementation or supporting configuration.
- [`requirements.txt`](requirements.txt): Implementation or supporting configuration.
- [`Dockerfile`](Dockerfile): Container build/service configuration.
- [`Makefile`](Makefile): Implementation or supporting configuration.
- [`docker-compose.yml`](docker-compose.yml): Container build/service configuration.
- [`tests/test_agent.py`](tests/test_agent.py): Executable checks and regression examples.

[PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md) contains the component diagram and the implementation walkthrough.

## 3. Can you walk through `run` and explain the decision it makes?

The main walkthrough here is `run(goal)` in [`src/cloudops/agent.py`](src/cloudops/agent.py#L16).

```python
def run(goal):
    trace = []
    text = goal.lower()
    if any(word in text for word in ("alert", "incident", "investigate", "memory", "down")):
        alerts = list_alerts()
        trace.append({"tool": "list_alerts", "result": alerts})
        service = alerts[0]["service"]
        trace.append({"tool": "read_logs", "result": read_logs(service)})
        trace.append({"tool": "check_manifest", "result": check_manifest(service)})
    return {
        "trace": trace,
        "answer": "Tools ran. This agent does not page and does not declare a root cause.",
        "paged": False,
        "confirmed_root_cause": False,
    }
```

The implementation calls `any`, `check_manifest`, `goal.lower`, `list_alerts`, `read_logs`, `trace.append`. In an interview, trace those calls in execution order using a fixture input.

## 4. What responsibility does `list_alerts` have?

`list_alerts()` is defined in [`src/cloudops/agent.py`](src/cloudops/agent.py#L4).

Its return expressions include:

- `ALERTS`

## 5. What input validation and failure behavior are implemented?

Explicit failure paths include:

- `HTTPException(status_code=404, detail='workspace not found')` in [`src/cloudops/ops.py`](src/cloudops/ops.py#L77).
- `HTTPException(status_code=404, detail='job not found')` in [`src/cloudops/ops.py`](src/cloudops/ops.py#L100).
- `HTTPException(status_code=404, detail='job not found')` in [`src/cloudops/ops.py`](src/cloudops/ops.py#L109).
- `HTTPException(status_code=403, detail='production apply is disabled in this lab')` in [`src/cloudops/ops.py`](src/cloudops/ops.py#L113).

I would test both the condition that reaches each exception and the caller that translates it. An explicit raise does not mean every malformed input or dependency failure is handled.

## 6. Which test would you use to demonstrate correctness?

[`tests/test_agent.py`](tests/test_agent.py#L8) contains `test_investigation_calls_three_tools_and_does_not_page`:

```python
def test_investigation_calls_three_tools_and_does_not_page():
    body = client.post("/agent/run", json={"goal": "investigate the billing memory alert"}).json()
    assert [step["tool"] for step in body["trace"]] == ["list_alerts", "read_logs", "check_manifest"]
    assert body["paged"] is False
    assert body["confirmed_root_cause"] is False
```

This is a concrete regression example from the repository. Its assertions establish that case; they do not establish behavior for every input or under production load.

## 7. What HTTP interface does the code expose?

- `POST /agent/run` → `agent_run` in [`src/cloudops/main.py`](src/cloudops/main.py#L16).
- `GET /readyz` → `readyz` in [`src/cloudops/ops.py`](src/cloudops/ops.py#L74).
- `POST /workspaces` → `create_workspace` in [`src/cloudops/ops.py`](src/cloudops/ops.py#L80).
- `GET /workspaces` → `list_workspaces` in [`src/cloudops/ops.py`](src/cloudops/ops.py#L98).
- `POST /workspaces/{workspace_id}/jobs` → `create_job` in [`src/cloudops/ops.py`](src/cloudops/ops.py#L106).
- `GET /jobs/{job_id}` → `get_job` in [`src/cloudops/ops.py`](src/cloudops/ops.py#L130).
- `POST /jobs/{job_id}/approve` → `approve_job` in [`src/cloudops/ops.py`](src/cloudops/ops.py#L140).
- `GET /audit` → `audit` in [`src/cloudops/ops.py`](src/cloudops/ops.py#L160).

These are literal decorators. Application/router prefixes, authentication, and middleware must be checked in the corresponding setup code.

## 8. Where does state live, and what happens with multiple workers?

Module-level containers include `ALERTS` in [`src/cloudops/agent.py`](src/cloudops/agent.py); `_WORKSPACES`, `_JOBS`, `_AUDIT`, `_METRICS` in [`src/cloudops/ops.py`](src/cloudops/ops.py).

These containers belong to a Python process. Inspect which are constant fixtures and which are mutated. Mutable process state needs an explicit shared-storage or synchronization strategy before multiple workers can provide consistent behavior.

## 9. How would another engineer reproduce your walkthrough?

Start from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

These commands follow repository manifests; environment setup and command results still need to be checked on the target machine.

## 10. What does automation verify, and what does it not prove?

Inspect [`.github/workflows/ci.yml`](.github/workflows/ci.yml) for triggers, permissions, and job commands. I would name the checks that those definitions run and show the latest run separately. A workflow definition alone does not establish a successful deployment, security review, or production SLO.

## 11. How would you present this project in a Forward Deployed Engineer interview?

Start with the user and operational problem described in [`README.md`](README.md). Explain one constraint that changes the implementation, show the linked code or example, and walk through a success case and a failure case. Agree on a measurable acceptance criterion before expanding the solution, and leave a handoff with data boundaries and rollback ownership. Any proposed production or business metric should be identified as a target until measured.

## 12. What is the input-to-output contract of `run`?

In [`src/cloudops/agent.py`](src/cloudops/agent.py#L16), `run(goal)` receives the inputs. The function computes these intermediate values:

- `trace = []`
- `text = goal.lower()`

Its result is defined by:

- `{'trace': trace, 'answer': 'Tools ran. This agent does not page and does not declare a root cause.', 'paged': False, 'confirmed_root_cause': False}`

## 13. Which decision rules or boundary conditions should an interviewer challenge?

The implementation in [`src/cloudops/agent.py`](src/cloudops/agent.py#L16) branches on:

- `any((word in text for word in ('alert', 'incident', 'investigate', 'memory', 'down')))`

A useful extension is a table-driven test that covers each condition just below, at, and above its boundary where applicable. These expressions are the current rules; changing them changes behavior and should be justified by the project’s acceptance criteria.

## 14. What does the operations plane add, and where is its limit?

[`src/cloudops/ops.py`](src/cloudops/ops.py) declares `GET /readyz`, `POST /workspaces`, `GET /workspaces`, `POST /workspaces/{workspace_id}/jobs`, `GET /jobs/{job_id}`, `POST /jobs/{job_id}/approve`, `GET /audit`, `GET /metrics`. Inspect the application’s `include_router` call for its URL prefix.

Its state containers are `_WORKSPACES`, `_JOBS`, `_AUDIT`, `_METRICS`. The job-approval handler defines whether a target is accepted or refused; check that branch and the associated tests instead of treating a recorded job as a successful infrastructure apply.
