from aws_lambda_powertools import Logger, Tracer

from event_notifier.client import ShitNotifierClient
from event_notifier.models import NotifyLevel, NotificationTopic

logger = Logger()
tracer = Tracer()


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def post_confirmation_trigger(event, _):
    try:
        logger.info(f"triggerSource: {event['triggerSource']}")
        if event['triggerSource'] != "PostConfirmation_ConfirmSignUp":
            return event

        client = ShitNotifierClient()
        client.send(
            level=NotifyLevel.INFO,
            service="backoffice",
            message=f"{event['request']['userAttributes']['given_name']} acabou de se registrar!",
            topic=NotificationTopic.COGNITO
        )
    except Exception as ex:
        logger.exception("CAUGHT EXCEPTION: ", ex)

    return event
