ALERTS = [{"service": "billing", "name": "HighMemory"}]


def list_alerts():
    return ALERTS


def read_logs(service):
    return f"{service} OOMKilled while memory was at 94 percent"


def check_manifest(service):
    return f"{service} container has no memory limit"


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
