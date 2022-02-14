from application.models.friend import FriendRequest, RequestType, FriendsList
from application.ports.friend_list_repository import FriendsListRepository
from goatcommons.notifications.client import PushNotificationsClient
from goatcommons.notifications.models import NotificationRequest


def friend_request_handler(
        request: FriendRequest,
        repository: FriendsListRepository,
        push_client: PushNotificationsClient
):
    friends_list = None
    if request.type_ == RequestType.FROM:
        friends_list = repository.find_by_subject(request.from_.sub) or FriendsList(request.from_.sub)
        if not friends_list.user_exists_on_list(request.to):
            friends_list.add_friend_invite(request.to)
    elif request.type_ == RequestType.TO:
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

    if friends_list:
        repository.save(friends_list)
