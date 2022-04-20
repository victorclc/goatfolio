import logging
import os
from typing import Dict

import requests

from models import NotifyRequest
from src.models import NotificationTopic

logger = logging.getLogger()

WEBHOOK_CONFIG: Dict[str, str] = {
    NotificationTopic.DEFAULT.name: os.getenv("DEFAULT_WEBHOOK_URL"),
    NotificationTopic.COGNITO.name: os.getenv("COGNITO_WEBHOOK_URL")
}

LEVEL_COLOR_MAP = {
    "INFO": 0xffffff,
    "WARNING": 0xffe203,
    "ERROR": 0xff7803,
    "CRITICAL": 0x8f000c,
}


def notify(request: NotifyRequest):
    payload = {
        "embeds": [
            {
                "title": f"{request.level} EVENT | {request.service}",
                "description": "",
                "color": LEVEL_COLOR_MAP[request.level],
                "fields": [
                    {
                        "name": "Service",
                        "value": request.service,
                        "inline": True
                    },
                    {
                        "name": "Level",
                        "value": request.level,
                        "inline": True
                    },
                    {
                        "name": "Message",
                        "value": request.message,
                        "inline": False
                    }
                ]

            }
        ]
    }
    response = requests.post(WEBHOOK_CONFIG[request.topic.name], json=payload)
    logger.info(f"Response: {response.content}")
