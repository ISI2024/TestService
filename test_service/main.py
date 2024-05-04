import logging
import sys
import asyncio
from test_service.queue_manager import QueueManager

sys.path.append("./..")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from test_service.endpoints import router as research_router
from test_service.database import Base, engine


def setup_logging():
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    rootLogger = logging.getLogger()

    fileHandler = logging.FileHandler("{0}/{1}.log".format("./logs", "test_service"))
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)


#setup_logging()

app = FastAPI(title="Test service")

app.include_router(research_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(engine)


@app.on_event("startup")
async def startup_event():
    manager = QueueManager()
    await manager.setup()

    task = asyncio.create_task(manager.consume())
    app.state.rabbitmq_task = task


@app.on_event("shutdown")
async def shutdown_event():
    app.state.rabbitmq_task.cancel()
    await app.state.rabbitmq_task
