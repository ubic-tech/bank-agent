from uuid import UUID
from typing import List, Union
from datetime import timedelta

from pydantic import BaseModel

from models.common import Shares


class StatusResponse(BaseModel):
    code: int
    message: str


class QuotaRequest(BaseModel):
    num_clients: int


class QuotaResponse(BaseModel):
    transaction_id: UUID
    partners: List[UUID]


class NoQuotaResponse(BaseModel):
    back_in: timedelta


class ReconstructRequest(BaseModel):
    transaction_id: UUID
    shares: Shares


class Endpoint(BaseModel):
    id: UUID
    endpoint: str


class EndpointRequest(BaseModel):
    partners: List[UUID]


class EndpointResponse(BaseModel):
    endpoints: List[Endpoint]


class ResultRequest(BaseModel):
    transaction_id: UUID


class ResultResponse(BaseModel):
    transaction_id: UUID
    result: Union[Shares, str]
