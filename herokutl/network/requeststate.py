import asyncio

from ..tl.tlobject import (
    _raise_if_forbidden_serialized_request,
    _verify_security_integrity,
)


class RequestState:
    """
    This request state holds several information relevant to sent messages,
    in particular the message ID assigned to the request, the container ID
    it belongs to, the request itself, the request as bytes, and the future
    result that will eventually be resolved.
    """

    __slots__ = ("container_id", "msg_id", "request", "data", "future", "after")

    def __init__(self, request, after=None):
        self.container_id = None
        self.msg_id = None
        self.request = request
        self.data = bytes(request)
        # check_serialized runs inside _raise_if_forbidden_serialized_request
        # (which additionally bans raw users.getUsers(InputUserSelf)), so a
        # direct identical scan here was a pure duplicate
        _verify_security_integrity()
        _raise_if_forbidden_serialized_request(request, self.data)
        self.future = asyncio.Future()
        self.after = after
