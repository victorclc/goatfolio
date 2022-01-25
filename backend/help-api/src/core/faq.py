from typing import Optional, Protocol, List

from src.application.models.question import Faq


class FaqRepository(Protocol):
    def find_all(self) -> List[Faq]:
        ...

    def find(self, topic: str) -> Faq:
        ...


def get_faq(topic: Optional[str], repository: FaqRepository):
    if topic:
        return repository.find(topic)
    return repository.find_all()
