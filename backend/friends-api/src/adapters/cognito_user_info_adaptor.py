from typing import List, Optional

import boto3

from application.models.user import User
from application.ports.user_info import UserInfoPort


class CognitoUserInfoAdapter(UserInfoPort):
    def __init__(self):
        self._client = boto3.client("cognito-idp")
        self._user_pool = "sa-east-1_PhDIztXK0"  # TODO environment variable this up

    def get_user_info(self, email: str) -> Optional[User]:
        response = self._client.list_users(
            UserPoolId=self._user_pool,
            AttributesToGet=["given_name", "sub"],
            Filter=f'email ="{email}"',
        )
        if not response or not response["Users"]:
            return None
        attrs = {
            attr["Name"]: attr["Value"] for attr in response["Users"][0]["Attributes"]
        }

        return User(sub=attrs["sub"], name=attrs["given_name"], email=email)


if __name__ == "__main__":
    adapter = CognitoUserInfoAdapter()
    print(adapter.get_user_info("victorcortelc@gmail.com"))
