from fastapi import FastAPI
from pydantic import BaseModel

from cloudops.agent import run

app = FastAPI(title="CloudOps agent")


class Goal(BaseModel):
    goal: str


@app.post("/agent/run")
def agent_run(body: Goal):
    return run(body.goal)
