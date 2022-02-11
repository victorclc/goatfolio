from typing import Optional

import boto3
from boto3.dynamodb.conditions import Key

from application.models.friend import FriendsList
from application.ports.friend_list_repository import FriendsListRepository


class DynamoFriendsRepository(FriendsListRepository):
    def __init__(self):
        self.__table = boto3.resource("dynamodb").Table("Friends")

    def find_by_subject(self, subject) -> Optional[FriendsList]:
        result = self.__table.query(
            KeyConditionExpression=Key("subject").eq(subject)
        )
        if result["Items"]:
            return FriendsList(**result["Items"][0])

    def save(self, friends_list: FriendsList):
        self.__table.put_item(Item=friends_list.to_dict())
