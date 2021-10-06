import logging

import firebase_admin
from firebase_admin.messaging import APNSConfig, APNSPayload, Aps, Notification, MulticastMessage, send_multicast

from adapters import NotificationTokensRepository
from goatcommons.configuration.system_manager import ConfigurationClient
from goatcommons.notifications.models import NotificationRequest
from goatcommons.utils import JsonUtils
from models import UserTokens

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(funcName)s %(levelname)-s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class PushNotificationCore:
    def __init__(self):
        certificate = JsonUtils.load(ConfigurationClient().get_secret('firebase-credentials'))
        cred = firebase_admin.credentials.Certificate(certificate)
        firebase_admin.initialize_app(cred)
        self.token_repo = NotificationTokensRepository()

    def send_notification(self, request: NotificationRequest):
        assert request.title
        assert request.message
        user_tokens = self.token_repo.find_user_tokens(request.subject)
        if not user_tokens:
            logger.info(f'No token available for subject {request.subject}')
            return

        notification = Notification(request.title, request.message)
        apns_config = APNSConfig(payload=APNSPayload(Aps(content_available=True)))
        message = MulticastMessage(tokens=user_tokens.tokens, notification=notification, apns=apns_config)

        send_multicast(message)

    def register_token(self, subject, token):
        user_tokens = self.token_repo.find_user_tokens(subject) or UserTokens(subject)
        user_tokens.tokens.append(token)
        user_tokens.tokens = list(set(user_tokens.tokens))
        self.token_repo.save(user_tokens)

    def unregister_token(self, subject, token):
        user_tokens = self.token_repo.find_user_tokens(subject) or UserTokens(subject)
        user_tokens.tokens.remove(token)
        user_tokens.tokens = list(set(user_tokens.tokens))
        self.token_repo.save(user_tokens)
