from uuid import UUID
from typing import List, Union

from pydantic import BaseModel

from models.common import Shares


class ShareRequest(BaseModel):
    transaction_id: UUID
    partners: List[UUID]
    clients: List[UUID]
    shares: Shares


class ComputeRequest(BaseModel):
    clients: List[UUID]


class ComputeResponse(BaseModel):
    clients: List[UUID]
    result: Union[Shares, str]
