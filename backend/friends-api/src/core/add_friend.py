from application.exceptions.invalid_request import InvalidRequest
from application.exceptions.user_not_found import UserNotFound
from application.models.friend import FriendRequest
from application.models.user import User
from application.ports.friend_request_publisher import FriendRequestPublisher
from application.ports.user_info import UserInfoPort


def publish_friend_request(
    from_: User, to_email: str, info: UserInfoPort, publisher: FriendRequestPublisher
):
    to_user = info.get_user_info(to_email)
    if not to_user:
        raise UserNotFound("Usuário não encontrado.")
    if to_user.email == from_.email:
        raise InvalidRequest("Não é possivel adicionar você como amigo de você mesmo.")

    # TODO CRIAR ADAPTER DO BANCO
    # BUSCAR FRIEND LIST DO TO E DO FROM
    # ADICIONAR CARAS LA
    # SALVAR OS 2 NO BANCO
    # MANDAR PRA FILA PRA MANDAR NOTIFICACAO

    friend_request = FriendRequest(from_=from_, to=to_user)
    publisher.send(friend_request)
