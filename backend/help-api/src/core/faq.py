from typing import Optional, Protocol, List

from aws_lambda_powertools import Logger

from src.application.models.question import Faq

logger = Logger()


class FaqRepository(Protocol):
    def find_all(self) -> List[Faq]:
        ...

    def find(self, topic: str) -> Faq:
        ...


def get_faq(topic: Optional[str], repository: FaqRepository):
    logger.info(f"Getting FAQ, topic={topic}")
    if topic:
        return repository.find(topic)
    return repository.find_all()
