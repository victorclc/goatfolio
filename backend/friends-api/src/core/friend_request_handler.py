from typing import Callable, Dict

from application.models.friend import FriendRequest, RequestType, FriendsList
from application.ports.friend_list_repository import FriendsListRepository
from goatcommons.notifications.client import PushNotificationsClient
from goatcommons.notifications.models import NotificationRequest

RequestTypeHandler = Callable[[FriendRequest, FriendsListRepository, PushNotificationsClient], FriendsList]


def request_from_type_handler(request: FriendRequest, repository: FriendsListRepository, _) -> FriendsList:
    friends_list = repository.find_by_subject(request.from_.sub) or FriendsList(request.from_.sub)
    if not friends_list.user_exists_on_list(request.to):
        friends_list.add_friend_invite(request.to)
    return friends_list


def request_to_type_handler(request: FriendRequest,
                            repository: FriendsListRepository,
                            push_client: PushNotificationsClient) -> FriendsList:
    friends_list = repository.find_by_subject(request.to.sub) or FriendsList(request.to.sub)
    if not friends_list.user_exists_on_list(request.from_):
        friends_list.add_friend_request(request.from_)
        push_client.send(
            NotificationRequest(
                subject=request.to.sub,
                title="Pedido de compartilhamento",
                message=f"{request.from_.name} te convidou para compartilhar dados da rentabilidade."
            )
        )
    return friends_list


def request_accept_from_type_handler(request: FriendRequest,
                                     repository: FriendsListRepository,
                                     push_client: PushNotificationsClient) -> FriendsList:
    ...


def request_accept_to_type_handler(request: FriendRequest,
                                   repository: FriendsListRepository,
                                   push_client: PushNotificationsClient) -> FriendsList:
    ...


def request_decline_from_type_handler(request: FriendRequest,
                                      repository: FriendsListRepository,
                                      push_client: PushNotificationsClient) -> FriendsList:
    ...


def request_decline_to_type_handler(request: FriendRequest,
                                    repository: FriendsListRepository,
                                    push_client: PushNotificationsClient) -> FriendsList:
    ...


def request_cancel_from_type_handler(request: FriendRequest,
                                     repository: FriendsListRepository,
                                     push_client: PushNotificationsClient) -> FriendsList:
    ...


def request_cancel_to_type_handler(request: FriendRequest,
                                   repository: FriendsListRepository,
                                   push_client: PushNotificationsClient) -> FriendsList:
    ...


HANDLERS: Dict[RequestType, RequestTypeHandler] = {
    RequestType.FROM: request_from_type_handler,
    RequestType.TO: request_to_type_handler,
    RequestType.ACCEPT_FROM: request_accept_from_type_handler,
    RequestType.ACCEPT_TO: request_accept_to_type_handler,
    RequestType.DECLINE_FROM: request_decline_from_type_handler,
    RequestType.DECLINE_TO: request_decline_to_type_handler,
    RequestType.CANCEL_FROM: request_cancel_from_type_handler,
    RequestType.CANCEL_TO: request_cancel_to_type_handler
}


def friend_request_handler(
        request: FriendRequest,
        repository: FriendsListRepository,
        push_client: PushNotificationsClient
):
    friends_list = HANDLERS[request.type_](request, repository, push_client)

    if friends_list:
        repository.save(friends_list)
