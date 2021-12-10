import abc

from application.models.friend import FriendRequest


class FriendRequestPublisher(abc.ABC):
    @abc.abstractmethod
    def send(self, request: FriendRequest):
        ...
