import logging

import core
import goatcommons.utils.json as jsonutils
from models import NotifyRequest

logger = logging.getLogger()


def shit_notify_handler(event, context):
    logger.info(f'EVENT: {event}')

    for message in event['Records']:
        print(message)
        request = NotifyRequest(**jsonutils.load(message['body']))
        core.notify(request)

# message = {'messageId': 'aa9973d6-c716-4331-9447-7278e736be35', 'receiptHandle': 'AQEBqEu2Ddn7XgDS9xUdDCTlcG9y3kMGUzcddUftXN7Gm7daIpAIYblCvpTrffxol0wxtQG6rQlkXZhNCkgq9UTxTPZ/TYmgxUqxzxwBTEZuO9oPPP2GsPsxOwnbiXBU+IC/29CpqRpcoXlBFAphtnEK2DWXLge74m8b2EKyRU32z3FmYUdh8AAs9kzlm6TfZFIwdFyOzGkrdvRB+Cii0IMFd/EOF3pY6gUl+MJnW+ZWgI3F6r6t8Y3TG+ku6cd2egoStFpODU8RkaHSqJE8G3hs8psEUOqgjDhv8TxtLgDHV90GsvD1OMYGPiOQz5tC6xSGCww2RFQhXRI8L0DI71MMs9rkGHRR/2pmh01XRQQEMzp2peCFjPJe9k3t0jmyu6s3oMCqrWQTLeTSY1dwn1KyVA==', 'body': '{"level": "INFO", "service": "backoffice", "message": "2951fbae-eba9-4b3c-abc2-2703798f26ad acabou de se registrar!", "topic": "COGNITO"}', 'attributes': {'ApproximateReceiveCount': '7', 'AWSTraceHeader': 'Root=1-625f13f6-07bce93455d107a32c51bc9a;Parent=5aa2f128c67dc5a7;Sampled=1', 'SentTimestamp': '1650398198810', 'SenderId': 'AROASAORJHNPEIONM3XUO:backoffice-api-dev-postConfirmationTrigger', 'ApproximateFirstReceiveTimestamp': '1650398198810'}, 'messageAttributes': {}, 'md5OfBody': 'f8d888c5e5983c780d7a0526e817f0f0', 'eventSource': 'aws:sqs', 'eventSourceARN': 'arn:aws:sqs:sa-east-1:138414734174:EventsToNotify', 'awsRegion': 'sa-east-1'}
