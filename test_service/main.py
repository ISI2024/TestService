import logging
import sys
import asyncio
from test_service.queue_manager import KafkaConsumer

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
    consumer1 = KafkaConsumer(topic="users")
    await consumer1.setup()

    task1 = asyncio.create_task(consumer1.consume_messages())
    app.state.kafka_task = task1

    consumer2 = KafkaConsumer(topic="tests")
    await consumer2.setup()

    task2 = asyncio.create_task(consumer2.consume_messages())
    app.state.kafka_task = task2


@app.on_event("shutdown")
async def shutdown_event():
    app.state.kafka_task.cancel()
    await app.state.kafka_task
