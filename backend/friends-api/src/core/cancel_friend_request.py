from application.models.friend import RequestType, FriendRequest
from application.models.user import User
from application.ports.friend_request_publisher import FriendRequestPublisher


def cancel_friend_request(from_user: User,
                          to_user: User,
                          publisher: FriendRequestPublisher):
    to_request = FriendRequest(from_user, to_user, RequestType.CANCEL_TO)
    from_request = FriendRequest(from_user, to_user, RequestType.CANCEL_FROM)

    publisher.send(to_request)
    publisher.send(from_request)
