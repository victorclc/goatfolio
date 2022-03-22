from application.ports.friend_list_repository import FriendsListRepository
from application.ports.rentability_calculator import RentabilityCalculator


def get_friends_rentability(subject: str, repository: FriendsListRepository, calculator: RentabilityCalculator):
    friends_list = repository.find_by_subject(subject)
    subjects = [f.user.sub for f in friends_list.friends] + [subject]
    performance = calculator.get_performance_for_subjects(subjects)

    # TODO TRANSFORMAR TODOS OS VALORES EM % ou ja trazer isso la do portoflio-api (melhor)
    # TODO RETORNAR LISTA ORDENADA POR MAIOR RENTABILIDADE PARA MENOR
    # TODO RETORNAR SUBJECT, VARIACAO NO DIA, VARIACAO NO MES, LISTA DOS TICKERS
