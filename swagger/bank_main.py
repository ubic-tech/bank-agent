from uuid import UUID
from typing import Iterable

from pydantic import BaseModel, Field, conlist
from fastapi import FastAPI, Header


Shares = conlist(int, min_items=1, max_items=1000,)


class StatusResponse(BaseModel):
    message: str = Field(
        ...,
        title="Сообщение о произошедшем.",
        description="Развернутоне сообщение об ошибке, статусе, etc.",
    )


class ShareRequest(BaseModel):
    transaction_id: UUID = Field(
        ...,
        title="Идентификатор транзакции (MPC-вычисления).",
        description=("Используется для сквозной идентиифкации текущего цикла вычислений. "
                     "Банк, который инициирует запрос, генерирует этот UUID и запрашивает "
                     "квоту на вычисления.")
    )
    partners: Iterable[UUID] = Field(
        ...,
        title="Идентификаторы банков-партнеров",
        description=("Идентификаторы банков-партнеров, которые будут "
                     "участвовать в текущем цикле вычислений.")
    )
    clients: Iterable[str] = Field(
        ...,
        title="Идентификаторов клиентов",
        description=("Список идентификаторов клиентов, для которых выполняется запрос."
                     "О форме идентификатора договоримся отдельно. Рабочая версия – "
                     "SHA-256 хэш от нормализованных ФИОДР.")
    )
    shares: Shares = Field(
        ...,
        title="Разделения секретов слагаемых.",
        description="По одному на каждого клиента, которые вошли в квоту вычислений."
    )

    class Config:
        schema_extra = {
            "example": {
                "transaction_id": "040138d2-cf3f-4587-a8c0-85d446c3d278",
                "partners": [
                    "d3871a32-0af6-4bbf-bdd2-835a4d8b919e",
                    "d769fe41-8ca7-4a7e-8b0a-612d660f7075",
                    "34d493b0-6acc-4e94-8024-422203c3692e",
                ],
                "clients": [
                    "6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b",
                    "d4735e3a265e16eee03f59718b9b5d03019c07d8b6c51f90da3a666eec13ab35",
                    "4e07408562bedb8b60ce05c1decfe3ad16b72230967de01f640b7e4729b49fce",
                ],
                "shares": [
                        0,
                        0,
                        0,
                ]
            }
        }


class ComputeRequest(BaseModel):
    clients: Iterable[str] = Field(
        ...,
        title="Идентификаторов клиентов.",
        description=("Список идентификаторов клиентов, для которых выполняется запрос."
                     "О форме идентификатора договоримся отдельно. Рабочая версия – "
                     "SHA-256 хэш от нормализованных ФИОДР.")
    )

    class Config:
        schema_extra = {
            "example": {
                "clients": [
                    "6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b",
                    "d4735e3a265e16eee03f59718b9b5d03019c07d8b6c51f90da3a666eec13ab35",
                    "4e07408562bedb8b60ce05c1decfe3ad16b72230967de01f640b7e4729b49fce",
                ],
            }
        }

app = FastAPI(
    title="MPC UBIC Service for Banks.",
    description="API сервиса Банков."
)


@app.post("/v1/share",
          response_model=StatusResponse,
          summary="Передача долей секретов.",
          )
def share(sr: ShareRequest,
          x_share_owner: UUID = Header(
            None, description="UUID банка, который передает доли секретов."
          )):
    return None


@app.get("/v1/checkup",
         response_model=StatusResponse,
         summary="Проверка доступности сервиса.")
def checkup():
    return None


@app.post("/v1/internal/compute",
          response_model=StatusResponse,
          summary="Инициировать процесс вычислений для списка клиентов.",
          description=("Внутренний метод. Доступен только банку, у которого "
                       "исполняется агент. Метод инициирует каскад вызовов "
                       "внешних методов, отвечающих за цикл вычислений."))
def compute(cr: ComputeRequest):
    return None
