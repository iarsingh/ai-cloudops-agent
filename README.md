# AI CloudOps agent

<!-- project-guide:start -->
## Project guide

[Project architecture](PROJECT_ARCHITECTURE.md) · [Interview questions and answers](INTERVIEW_QA.md)

Use the architecture document for the component diagram, implementation boundaries, and verification entry points. The interview guide includes source-backed answers and project walkthroughs.

### Implementation map

| Component | Responsibility |
| --- | --- |
| [`src/cloudops/main.py`](src/cloudops/main.py) | HTTP handlers: `POST /agent/run` |
| [`src/cloudops/agent.py`](src/cloudops/agent.py) | Functions: `list_alerts`, `read_logs`, `check_manifest`, `run` |
| [`requirements.txt`](requirements.txt) | Implementation or supporting configuration |
| [`tests/test_agent.py`](tests/test_agent.py) | Executable checks and regression examples |
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | GitHub Actions job definitions |
| [`README.md`](README.md) | Project explanations or operating notes |

### Local setup and verification

From the repository root (the commands follow the checked-in manifests):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

To serve the FastAPI application locally, install the server separately if it is not already available:

```bash
python -m pip install uvicorn
PYTHONPATH=src python -m uvicorn cloudops.main:app --reload
```

<!-- project-guide:end -->

Level: Advanced+

Skills: Tool calling, a tool schema, Kubernetes signals, logs

`POST /agent/run` reads the goal. An investigation calls three tools in order: list alerts, read logs, check the manifest. The tool list is `mcp/tools.json`.

The answer says the tools ran. `paged` and `confirmed_root_cause` stay false. There is no hosted model. The loop is deterministic so a test can name the tool order.

```bash
pip install -r requirements.txt
pytest -q
```

## Ops plane

Workspaces, tenant isolation, job approval, and audit live under `/v1`. Production apply is refused. See `docs/ARCHITECTURE.md`.
