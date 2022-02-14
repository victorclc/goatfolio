from typing import Optional

from application.models.friend import FriendsList
from application.ports.friend_list_repository import FriendsListRepository


def get_friends_list(subject: str, repository: FriendsListRepository) -> Optional[FriendsList]:
    return repository.find_by_subject(subject)
