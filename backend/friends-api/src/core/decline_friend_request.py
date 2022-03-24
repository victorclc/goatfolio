from application.models.friend import FriendRequest, RequestType
from application.models.user import User
from application.ports.friend_request_publisher import FriendRequestPublisher


def decline_friend_request(from_user: User,
                           to_user: User,
                           publisher: FriendRequestPublisher):
    to_request = FriendRequest(from_user, to_user, RequestType.DECLINE_TO)
    from_request = FriendRequest(from_user, to_user, RequestType.DECLINE_FROM)

    publisher.send(to_request)
    publisher.send(from_request)
