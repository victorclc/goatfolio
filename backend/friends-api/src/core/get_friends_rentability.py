from typing import List

from adapters.out.dynamo_friend_list_repository import DynamoFriendsRepository
from adapters.out.rest_friends_rentability_adaptor import RESTRentabilityCalculator
from application.models.friend import FriendsList
from application.models.performance import UserRentability
from application.models.user import User
from application.ports.friend_list_repository import FriendsListRepository
from application.ports.rentability_calculator import RentabilityCalculator


def get_friends_rentability(from_user: User, repository: FriendsListRepository, calculator: RentabilityCalculator) -> \
        List[UserRentability]:
    friends_list = repository.find_by_subject(from_user.sub) or FriendsList(from_user.sub)
    subjects = [f.user.sub for f in friends_list.friends] + [from_user.sub]
    performance = calculator.get_performance_for_subjects(subjects)

    rentability = []
    for subject, performance in performance.items():
        if subject == from_user.sub:
            from_user.name = "Eu"
            rentability.append(UserRentability(from_user, performance))
        else:
            rentability.append(UserRentability(friends_list.get_user_from_subject(subject), performance))
    return rentability


if __name__ == '__main__':
    print(get_friends_rentability(User("629e4155-8f6c-41da-9d59-d718817c798e", None, None), DynamoFriendsRepository(),
                                  RESTRentabilityCalculator()))
