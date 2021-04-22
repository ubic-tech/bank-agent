from uuid import UUID
from typing import Union, Optional

from asyncio import exceptions
from fastapi import APIRouter, Header, Response, status
from pydantic.error_wrappers import ValidationError
from aiocache import cached
import time

from models import bank, ubic, common
from config import config
from utils import request
from repository.fake_repository import FakeRepository
from utils.decompose import decompose
from transaction_manager import (
    TransactionManager, NotSinglePartnerShare, ShareAlreadyReceived)

router = APIRouter()
repository = FakeRepository(UUID(config.BANK_UUID))
transaction_manager = TransactionManager()


class NoQuotaException(Exception):
    def __init__(self, no_quota_response: ubic.NoQuotaResponse):
        self.no_quota_response = no_quota_response


def make_header() -> {str: UUID}:
    return {"x-share-owner": config.BANK_UUID} \
        if config.OWNER_UUID_HEADER else {}


@cached(ttl=config.ENDPOINTS_CACHE_TTL)
async def get_endpoints_by_uuid(uuids: [UUID]) -> [str]:
    endpoints_request = ubic.EndpointRequest(partners=uuids)
    resp = await request.request(config.ENDPOINTS_ROUTE,
                                 headers=make_header(),
                                 data=endpoints_request.json(),
                                 timeout=config.REQUEST_TIMEOUT)
    try:
        endpoints = ubic.EndpointResponse(**resp).endpoints
        return [ep.endpoint for ep in endpoints]
    except (ValidationError, IndexError):
        raise request.OperationError


def _create_shares(transaction_id: UUID, partners: [UUID], clients: [UUID]
                   ) -> (bank.ShareRequest, [bank.ShareRequest]):
    """
    :return: my share and shares for partners
    """
    res: [bank.ShareRequest] = []
    decomposed_balances: [[int]] = []
    shares_count = len(partners)
    balances = repository.get_balances(clients)
    for balance in balances:
        decomposed_balances.append(decompose(balance, shares_count))

    for i in range(shares_count):
        res.append(bank.ShareRequest(
            transaction_id=transaction_id,
            partners=partners,
            clients=clients,
            shares=[b[i] for b in decomposed_balances])
        )
    return res[0], res[1:]


async def _launch_mpc(transaction_id: UUID, partners: [UUID], clients: [UUID]):
    endpoints = await get_endpoints_by_uuid(
        [p for p in partners if p != UUID(config.BANK_UUID)])  # my endpoint is not required

    my_share, partner_shares = _create_shares(transaction_id,
                                              partners,
                                              clients)

    await transaction_manager.add_transaction(
        transaction_id=transaction_id,
        partners=partners,
        my_share=my_share.shares
    )

    for (endpoint, partner_share) in zip(endpoints, partner_shares):
        try:
            await request.request(endpoint + config.SHARES_ROUTE,
                                  headers=make_header(),
                                  data=partner_share.json(),
                                  timeout=config.REQUEST_TIMEOUT)
        except request.StatusError:
            pass


async def _share(share_request: bank.ShareRequest, x_share_owner: UUID):
    tid = share_request.transaction_id

    if not await transaction_manager.find(tid):
        await _launch_mpc(tid, share_request.partners, share_request.clients)

    try:
        await transaction_manager.add_partner_share(
            transaction_id=tid,
            partner_id=x_share_owner,
            shares=share_request.shares
        )
    except (NotSinglePartnerShare, ShareAlreadyReceived):
        return

    reconstructed = await transaction_manager.get_shares_if_ready(tid)
    if reconstructed is None:
        return

    reconstruct_request = ubic.ReconstructRequest(
        transaction_id=tid,
        shares=reconstructed
    )

    try:
        await request.request(
            config.RECONSTRUCT_ROUTE,
            headers=make_header(),
            data=reconstruct_request.json(),
            timeout=config.REQUEST_TIMEOUT
        )
    except request.StatusError:
        pass


async def _start_compute(compute_request: bank.ComputeRequest
                         ) -> UUID:
    quota_request = ubic.QuotaRequest(
        num_clients=len(compute_request.clients)
    )

    resp = await request.request(
        config.QUOTA_ROUTE,
        headers=make_header(),
        data=quota_request.json(),
        timeout=config.REQUEST_TIMEOUT)
    try:
        quota_resp = ubic.QuotaResponse(**resp)
    except ValidationError:
        raise NoQuotaException(no_quota_response=ubic.NoQuotaResponse(**resp))

    if UUID(config.BANK_UUID) not in quota_resp.partners:
        quota_resp.partners.append(UUID(config.BANK_UUID))

    await _launch_mpc(quota_resp.transaction_id,
                      quota_resp.partners,
                      compute_request.clients)
    return quota_resp.transaction_id


@router.post("/compute",
             response_model=Union[bank.ComputeResponse,
                                  ubic.NoQuotaResponse],
             response_model_exclude_unset=True)
async def compute(compute_request: bank.ComputeRequest, response: Response):
    start = time.time()
    try:
        tid = await _start_compute(compute_request)
    except NoQuotaException as exc:
        return exc.no_quota_response
    except exceptions.TimeoutError:
        response.status_code = status.HTTP_408_REQUEST_TIMEOUT
        return

    res_request = ubic.ResultRequest(transaction_id=tid)
    response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    while True:
        remained = float(config.COMPUTE_TIMEOUT) - (time.time() - start)
        if remained <= 0:
            response.status_code = status.HTTP_408_REQUEST_TIMEOUT
            return
        try:
            resp = await request.request(config.RESULT_ROUTE,
                                         headers=make_header(),
                                         data=res_request.json(),
                                         timeout=remained)
        except (exceptions.TimeoutError, request.RequestTimeout):
            response.status_code = status.HTTP_408_REQUEST_TIMEOUT
            return
        except request.NotFound:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return
        except request.AcceptedButNotReady:
            continue
        response.status_code = status.HTTP_200_OK
        res = ubic.ResultResponse(**resp)
        return bank.ComputeResponse(
            clients=compute_request.clients,
            result=res.result
        )


@router.post("/share",
             response_model=common.StatusResponse,
             response_model_exclude_unset=True)
async def share(share_request: bank.ShareRequest,
                x_share_owner: Optional[UUID] = Header(None)):
    await _share(share_request=share_request, x_share_owner=x_share_owner)
    return common.StatusResponse(code=200, message="OK")
