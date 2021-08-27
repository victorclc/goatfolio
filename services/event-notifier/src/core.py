import os
import requests

from models import NotifyRequest


class EventNotifierCore:
    WEBHOOK_URL = os.getenv(f'{os.getenv("STAGE")}_WEBHOOK_URL')
    LEVEL_COLOR_MAP = {
        "INFO": 0xffffff,
        "WARNING": 0xffe203,
        "ERROR": 0xff7803,
        "CRITICAL": 0x8f000c,
    }

    def notify(self, request: NotifyRequest):
        payload = {
            "embeds": [
                {
                    "title": f"{request.level} EVENT | {request.service}",
                    "description": "",
                    "color": self.LEVEL_COLOR_MAP[request.level],
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
        requests.post(self.WEBHOOK_URL, json=payload)
