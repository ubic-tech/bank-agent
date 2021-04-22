import aiohttp


_accepted_but_not_ready = 202
_request_timeout = 408
_not_found = 404


class OperationError(Exception):
    pass


class StatusError(Exception):
    pass


class AcceptedButNotReady(Exception):
    pass


class RequestTimeout(Exception):
    pass


class NotFound(Exception):
    pass


async def request(url, *, method='post', expected_status=200, **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.request(url=url, method=method, **kwargs) as resp:
            if resp == _accepted_but_not_ready:
                raise AcceptedButNotReady(resp.status, await resp.text())
            elif resp.status == _request_timeout:
                raise RequestTimeout()
            elif resp.status == _not_found:
                raise NotFound()
            elif resp.status != expected_status:
                raise StatusError(resp.status, await resp.text())
            return await resp.json()
