from application.models.friend import FriendRequest, RequestType, FriendsList
from application.ports.friend_list_repository import FriendsListRepository


def friend_request_handler(
        request: FriendRequest,
        repository: FriendsListRepository
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
            # SEND TO PUSH NOTIFICATIONS

    if friends_list:
        repository.save(friends_list)
