from pydantic import BaseModel, conlist


Shares = conlist(int, min_items=1, max_items=1000)


class StatusResponse(BaseModel):
    code: int
    message: str
