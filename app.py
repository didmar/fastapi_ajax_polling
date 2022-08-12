import asyncio
import logging
from concurrent.futures.process import ProcessPoolExecutor
from typing import Dict
from uuid import UUID, uuid4

from fastapi import BackgroundTasks, Form, FastAPI, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field


class Job(BaseModel):
    uid: UUID = Field(default_factory=uuid4)
    status: str = "in_progress"
    result: int = None


jobs: Dict[UUID, Job] = {}


templates = Jinja2Templates(directory=".")
app = FastAPI()


async def run_in_process(fn, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(app.state.executor, fn, *args)  # wait and return result


def task(textinput):
    logging.info(f"Task starting: {textinput}")
    import time
    time.sleep(3)
    logging.info("Task done")
    return f"Hello {textinput}!"


async def start_cpu_bound_task(uid: UUID, param: int) -> None:
    jobs[uid].result = await run_in_process(task, param)
    jobs[uid].status = "complete"


@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/submit")
async def task_handler(background_tasks: BackgroundTasks, textinput: str = Form(default="World")):
    new_task = Job()
    jobs[new_task.uid] = new_task
    background_tasks.add_task(start_cpu_bound_task, new_task.uid, textinput)
    return RedirectResponse(f"/{new_task.uid}", status_code=status.HTTP_302_FOUND)


@app.get("/{uid}", response_class=HTMLResponse)
def result_page(request: Request, uid: UUID):
    return templates.TemplateResponse("result.html", {"request": request, "uid": uid})


@app.get("/status/{uid}")
async def status_handler(uid: UUID):
    return jobs[uid]


@app.on_event("startup")
async def startup_event():
    app.state.executor = ProcessPoolExecutor()


@app.on_event("shutdown")
async def on_shutdown():
    app.state.executor.shutdown()
