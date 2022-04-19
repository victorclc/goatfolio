from aws_lambda_powertools import Logger, Tracer

from event_notifier.client import ShitNotifierClient
from event_notifier.models import NotifyLevel, NotificationTopic

logger = Logger()
tracer = Tracer()


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def post_confirmation_trigger(event, _):
    logger.info(f"triggerSource: {event['triggerSource']}")
    if event['triggerSource'] != "PostConfirmation_ConfirmSignUp":
        return event

    client = ShitNotifierClient()
    client.send(
        level=NotifyLevel.INFO,
        service="backoffice",
        message=f"{event['userName']} acabou de se registrar!",
        topic=NotificationTopic.COGNITO
    )

    return event
