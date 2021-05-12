from fastapi import FastAPI
from tests.ubic_stub.router import router

app = FastAPI()
app.include_router(
    router,
    prefix="/v1"
)
