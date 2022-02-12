from application.exceptions.invalid_request import InvalidRequest
from application.exceptions.user_not_found import UserNotFound
from application.models.friend import FriendRequest, RequestType
from application.models.user import User
from application.ports.friend_request_publisher import FriendRequestPublisher
from application.ports.user_info import UserInfoPort


def publish_friend_request(
        from_user: User,
        to_email: str,
        info: UserInfoPort,
        publisher: FriendRequestPublisher
):
    to_user = info.get_user_info(to_email)
    if not to_user:
        raise UserNotFound("Usuário não encontrado.")
    if to_user.email == from_user.email:
        raise InvalidRequest("Não é possivel compartilhar com você mesmo.")

    to_request = FriendRequest(from_=from_user, to=to_user, type_=RequestType.TO)
    from_request = FriendRequest(from_=from_user, to=to_user, type_=RequestType.FROM)

    publisher.send(to_request)
    publisher.send(from_request)

    # from_list = repository.find_by_subject(from_user.sub) or FriendsList(from_user.sub)
    # from_list.add_friend_invite(to_user)
    #
    # to_list = repository.find_by_subject(to_user.sub) or FriendsList(to_user.sub)
    # to_list.add_friend_request(from_user)
    #
    # repository.save(from_list)
    # repository.save(to_list)
    #
    # # TODO CRIAR ADAPTER DO BANCO
    # # BUSCAR FRIEND LIST DO TO E DO FROM
    # # ADICIONAR CARAS LA
    # # SALVAR OS 2 NO BANCO
    # # MANDAR PRA FILA PRA MANDAR NOTIFICACAO
