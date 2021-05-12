import uuid
from typing import Union

from fastapi import APIRouter

from tests.ubic_stub.endpoints import ENDPOINTS
from models import ubic as models
from models.common import StatusResponse
from tests.ubic_stub.transaction_manager import TransactionManager

router = APIRouter()
transaction_manager = TransactionManager()


@router.post("/quota",
             response_model=Union[models.QuotaResponse, models.NoQuotaResponse],
             response_model_exclude_unset=True)
def quota(quota_request: models.QuotaRequest):
    # return models.NoQuotaResponse(back_in=timedelta(seconds=100500))
    transaction_id = uuid.uuid4()
    # transaction_id = uuid.UUID("111aaaaa-1af0-489e-b761-d40344c12e70")

    partners = [uid for uid in ENDPOINTS.keys()]
    transaction_manager.add(transaction_id,
                            len(partners),
                            quota_request.num_clients)
    return models.QuotaResponse(
        transaction_id=transaction_id,
        partners=[uid for uid in ENDPOINTS.keys()]
    )


@router.post("/reconstruct",
             response_model=StatusResponse,
             response_model_exclude_unset=True)
def reconstruct(reconstruct_request: models.ReconstructRequest):
    transaction_manager.sum_up(reconstruct_request.transaction_id,
                               reconstruct_request.shares)
    return StatusResponse(code=200, message="OK")


@router.post("/result",
             response_model=Union[models.ResultResponse, StatusResponse],
             response_model_exclude_unset=True)
async def result(result_request: models.ResultRequest):
    tid = result_request.transaction_id

    if not transaction_manager.find(tid):
        return StatusResponse(code=404,
                              message=f"no such transaction: {tid}")

    if not transaction_manager.ready(tid):
        return models.ResultResponse(transaction_id=tid, result="not ready")  # todo: parametrize? env var?

    return models.ResultResponse(transaction_id=tid,
                                 result=transaction_manager.get_shares(tid))


@router.post("/endpoints",
             response_model=models.EndpointResponse,
             response_model_exclude_unset=True)
def endpoints(endpoint_request: models.EndpointRequest):
    try:
        resp = [
            models.Endpoint(id=_id, endpoint=ENDPOINTS[_id])
            for _id in endpoint_request.partners
        ]
    except KeyError:
        return models.EndpointResponse(endpoints=[])
    return models.EndpointResponse(endpoints=resp)
