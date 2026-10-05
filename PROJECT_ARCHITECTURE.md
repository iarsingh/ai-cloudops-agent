# ai-cloudops-agent — project architecture

[README](README.md) · [Interview questions and answers](INTERVIEW_QA.md)

## Purpose and scope

`POST /agent/run` reads the goal. An investigation calls three tools in order: list alerts, read logs, check the manifest. The tool list is `mcp/tools.json`.

This document describes files and symbols in this checkout. Deployment templates and statements in the original overview are distinguished from a verified running environment.

## Component diagram

```mermaid
flowchart LR
    M0["src/cloudops/agent.py"]
    M1["src/cloudops/main.py"]
    M2["src/cloudops/ops.py"]
    M1 -->|imports| M0
    M1 -->|imports| M2
```

For Python repositories, arrows show resolved local imports, not network calls or deployment order. Otherwise the diagram is a repository component map; containment arrows do not assert runtime integration.

## Components and responsibilities

| Component | Responsibility |
| --- | --- |
| [`src/cloudops/main.py`](src/cloudops/main.py) | HTTP handlers: `POST /agent/run` |
| [`src/cloudops/ops.py`](src/cloudops/ops.py) | HTTP handlers: `GET /readyz`, `POST /workspaces`, `GET /workspaces`, `POST /workspaces/{workspace_id}/jobs`, `GET /jobs/{job_id}` |
| [`src/cloudops/agent.py`](src/cloudops/agent.py) | Functions: `list_alerts`, `read_logs`, `check_manifest`, `run` |
| [`requirements.txt`](requirements.txt) | Implementation or supporting configuration |
| [`Dockerfile`](Dockerfile) | Container build/service configuration |
| [`Makefile`](Makefile) | Implementation or supporting configuration |
| [`docker-compose.yml`](docker-compose.yml) | Container build/service configuration |
| [`tests/test_agent.py`](tests/test_agent.py) | Executable checks and regression examples |
| [`tests/test_ops.py`](tests/test_ops.py) | Executable checks and regression examples |
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | GitHub Actions job definitions |
| [`README.md`](README.md) | Project explanations or operating notes |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Project explanations or operating notes |

## Existing design and operating guides

These checked-in guides provide the project’s detailed design, operational context, or deployment view:

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Request interface

| Method and path | Handler | Source |
| --- | --- | --- |
| `POST /agent/run` | `agent_run` | [`src/cloudops/main.py`](src/cloudops/main.py#L16) |
| `GET /readyz` | `readyz` | [`src/cloudops/ops.py`](src/cloudops/ops.py#L44) |
| `POST /workspaces` | `create_workspace` | [`src/cloudops/ops.py`](src/cloudops/ops.py#L49) |
| `GET /workspaces` | `list_workspaces` | [`src/cloudops/ops.py`](src/cloudops/ops.py#L66) |
| `POST /workspaces/{workspace_id}/jobs` | `create_job` | [`src/cloudops/ops.py`](src/cloudops/ops.py#L73) |
| `GET /jobs/{job_id}` | `get_job` | [`src/cloudops/ops.py`](src/cloudops/ops.py#L96) |
| `POST /jobs/{job_id}/approve` | `approve_job` | [`src/cloudops/ops.py`](src/cloudops/ops.py#L105) |
| `GET /audit` | `audit` | [`src/cloudops/ops.py`](src/cloudops/ops.py#L122) |
| `GET /metrics` | `metrics` | [`src/cloudops/ops.py`](src/cloudops/ops.py#L138) |

The table lists literal route decorators found in the inspected Python modules. Router prefixes and middleware can add behavior; check the linked handler and application setup before calling an endpoint.

## Implementation walkthrough

### `run(goal)`

Source: [`src/cloudops/agent.py`](src/cloudops/agent.py#L16).

Calls visible in this function: `any`, `check_manifest`, `goal.lower`, `list_alerts`, `read_logs`, `trace.append`.

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

### `list_alerts()`

Source: [`src/cloudops/agent.py`](src/cloudops/agent.py#L4).

```python
def list_alerts():
    return ALERTS
```

### `read_logs(service)`

Source: [`src/cloudops/agent.py`](src/cloudops/agent.py#L8).

```python
def read_logs(service):
    return f"{service} OOMKilled while memory was at 94 percent"
```

### `check_manifest(service)`

Source: [`src/cloudops/agent.py`](src/cloudops/agent.py#L12).

```python
def check_manifest(service):
    return f"{service} container has no memory limit"
```

## Validation and failure paths

| Explicit exception | Source |
| --- | --- |
| `HTTPException(status_code=404, detail='workspace not found')` | [`src/cloudops/ops.py`](src/cloudops/ops.py#L77) |
| `HTTPException(status_code=404, detail='job not found')` | [`src/cloudops/ops.py`](src/cloudops/ops.py#L100) |
| `HTTPException(status_code=404, detail='job not found')` | [`src/cloudops/ops.py`](src/cloudops/ops.py#L109) |
| `HTTPException(status_code=403, detail='production apply is disabled in this lab')` | [`src/cloudops/ops.py`](src/cloudops/ops.py#L113) |

These are explicit exceptions in the inspected source, rather than a claim that every failure is handled. Follow the calling handler to see whether the exception becomes an HTTP response or propagates.

## Data and state

- [`src/cloudops/agent.py`](src/cloudops/agent.py) defines module-level containers: `ALERTS`.
- [`src/cloudops/ops.py`](src/cloudops/ops.py) defines module-level containers: `_WORKSPACES`, `_JOBS`, `_AUDIT`, `_METRICS`.

Module-level dictionaries/lists live in a Python process. They can be fixtures or mutable state; inspect writes before treating them as persistent storage. A production extension would need to define persistence and concurrency behavior explicitly.

## Data flow and design decisions

### What is the input-to-output contract of `run`

In [`src/cloudops/agent.py`](src/cloudops/agent.py#L16), `run(goal)` receives the inputs. The function computes these intermediate values:

- `trace = []`
- `text = goal.lower()`

Its result is defined by:

- `{'trace': trace, 'answer': 'Tools ran. This agent does not page and does not declare a root cause.', 'paged': False, 'confirmed_root_cause': False}`

### Which decision rules or boundary conditions should an interviewer challenge

The implementation in [`src/cloudops/agent.py`](src/cloudops/agent.py#L16) branches on:

- `any((word in text for word in ('alert', 'incident', 'investigate', 'memory', 'down')))`

A useful extension is a table-driven test that covers each condition just below, at, and above its boundary where applicable. These expressions are the current rules; changing them changes behavior and should be justified by the project’s acceptance criteria.

### What does the operations plane add, and where is its limit

[`src/cloudops/ops.py`](src/cloudops/ops.py) declares `GET /readyz`, `POST /workspaces`, `GET /workspaces`, `POST /workspaces/{workspace_id}/jobs`, `GET /jobs/{job_id}`, `POST /jobs/{job_id}/approve`, `GET /audit`, `GET /metrics`. Inspect the application’s `include_router` call for its URL prefix.

Its state containers are `_WORKSPACES`, `_JOBS`, `_AUDIT`, `_METRICS`. The job-approval handler defines whether a target is accepted or refused; check that branch and the associated tests instead of treating a recorded job as a successful infrastructure apply.

## Setup and verification

The following commands are derived from the checked-in dependency/test contracts. Execute them from the repository root; the block prepares a local environment, not a cloud deployment.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

Python dependencies: [`requirements.txt`](requirements.txt).

Test entry points: [`tests/test_agent.py`](tests/test_agent.py), [`tests/test_ops.py`](tests/test_ops.py).

Automation definitions: [`.github/workflows/ci.yml`](.github/workflows/ci.yml). Read their triggers and job steps to determine what CI actually runs.

## Operating boundaries and design review

Before turning this checkout into a customer deployment, establish the input contract, data ownership, access controls, failure response, evaluation criteria, and rollback owner. Repository fixtures and unit tests demonstrate local behavior; they do not establish throughput, uptime, compliance, or business impact.

A useful architecture review starts with the linked implementation: identify where input enters, where a decision is made, which state can change, and which external dependency can fail. Add a deployment view only for infrastructure that is actually configured and exercised.
