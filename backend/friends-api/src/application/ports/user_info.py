import abc
from typing import Optional

from application.models.user import User


class UserInfoPort(abc.ABC):
    @abc.abstractmethod
    def get_user_info(self, email: str) -> Optional[User]:
        ...
