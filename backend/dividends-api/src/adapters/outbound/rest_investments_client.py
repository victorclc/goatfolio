import os
from http import HTTPStatus
from typing import List

from aws_lambda_powertools import Logger

import goatcommons.utils.json as jsonutils

import requests

from application.models.add_investment_request import AddInvestmentRequest
from goatcommons.configuration.system_manager import ConfigurationClient


class BatchSavingException(Exception):
    pass


class DeleteException(Exception):
    pass


logger = Logger()


class RestInvestmentsClient:
    BASE_URL = os.getenv("INVESTMENTS_BASE_API_URL")

    def __init__(self):
        config = ConfigurationClient()
        self.api_key = config.get_secret("investments-api-key")

    def delete(self, subject: str, _id: str):
        response = requests.delete(
            f"{self.BASE_URL}/private/delete",
            data=jsonutils.dump({"investment_id": _id, "subject": subject})
        )

        if response.status_code != HTTPStatus.OK:
            logger.error(f'Investment deletion error: {response.raw}')
            raise DeleteException(f"Investment deletion error: {response.raw}")

    def batch_save(self, add_requests: List[AddInvestmentRequest]):
        url = f'{self.BASE_URL}/investments/batch'

        body = list(map(lambda i: i.to_dict(), add_requests))
        response = requests.post(url, data=jsonutils.dump(body), headers={'x-api-key': self.api_key})

        if response.status_code != HTTPStatus.OK:
            logger.error(f'Batch save failed: {response}')
            raise BatchSavingException()
        return response
