# AI CloudOps agent

Level: Advanced+

Skills: Tool calling, a tool schema, Kubernetes signals, logs

`POST /agent/run` reads the goal. An investigation calls three tools in order: list alerts, read logs, check the manifest. The tool list is `mcp/tools.json`.

The answer says the tools ran. `paged` and `confirmed_root_cause` stay false. There is no hosted model. The loop is deterministic so a test can name the tool order.

```bash
pip install -r requirements.txt
pytest -q
```

