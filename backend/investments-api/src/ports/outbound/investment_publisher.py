from typing import Optional

from typing_extensions import Protocol

from domain.investment import Investment


class InvestmentPublisher(Protocol):
    def publish(
        self,
        subject: str,
        new_investment: Optional[Investment],
        old_investment: Optional[Investment],
    ):
        """Publish the investment """
