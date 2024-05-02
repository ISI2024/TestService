import logging
import sys

sys.path.append("./..")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from endpoints import router as research_router


def setup_logging():
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    rootLogger = logging.getLogger()

    fileHandler = logging.FileHandler("{0}/{1}.log".format("./logs", "test_service"))
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)


setup_logging()

app = FastAPI(root_path=None, title="Test service")

app.include_router(research_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
