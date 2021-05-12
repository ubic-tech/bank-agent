from uuid import UUID
from typing import List, Union

from pydantic import BaseModel

from models.common import Shares


class ShareRequest(BaseModel):
    transaction_id: UUID
    partners: List[UUID]
    clients: List[str]
    shares: Shares


class ComputeRequest(BaseModel):
    clients: List[str]


class ComputeResponse(BaseModel):
    clients: List[str]
    result: Union[Shares, str]
