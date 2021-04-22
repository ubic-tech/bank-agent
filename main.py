from datetime import datetime
from random import seed
import logging

from fastapi import FastAPI

from router import router
from config import config
from TransactionManager import create_transaction_manager


app = FastAPI()
app.include_router(
    router,
    prefix="/v1"
)


@app.on_event("startup")
async def init_app():
    await create_transaction_manager()
    seed(datetime.now().microsecond)
    logging.info(f"{config.BANK_UUID} launched")
