from typing import List

from application.models.performance import FriendRentability
from application.ports.friend_list_repository import FriendsListRepository
from application.ports.rentability_calculator import RentabilityCalculator


def get_friends_rentability(subject: str, repository: FriendsListRepository, calculator: RentabilityCalculator) -> \
        List[FriendRentability]:
    friends_list = repository.find_by_subject(subject)
    subjects = [f.user.sub for f in friends_list.friends] + [subject]
    performance = calculator.get_performance_for_subjects(subjects)

    rentability = []
    for subject, performance in performance.items():
        rentability.append(FriendRentability(friends_list.get_friend_from_subject(subject), performance))

    return rentability
