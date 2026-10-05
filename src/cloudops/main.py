from cloudops.ops import router as ops_router
from fastapi import FastAPI
from pydantic import BaseModel

from cloudops.agent import run

app = FastAPI(title="CloudOps agent")
app.include_router(ops_router, prefix="/v1")


class Goal(BaseModel):
    goal: str


@app.post("/agent/run")
def agent_run(body: Goal):
    return run(body.goal)
