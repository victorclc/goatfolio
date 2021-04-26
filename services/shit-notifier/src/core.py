import os
import requests

from models import NotifyRequest


class ShitNotifierCore:
    WEBHOOK_URL = os.getenv('WEBHOOK_URL')

    def notify(self, request: NotifyRequest):
        requests.post(self.WEBHOOK_URL, json={
            'content': f'###################################\nLevel: {request.level}\nService: {request.service}\nMessage: {request.message}\n###################################'})
