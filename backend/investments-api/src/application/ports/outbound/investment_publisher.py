from typing import Optional

from typing import Protocol

from application.investment import Investment


class InvestmentPublisher(Protocol):
    def publish(
        self,
        subject: str,
        updated_timestamp: int,
        new_investment: Optional[Investment],
        old_investment: Optional[Investment],
    ):
        """Publish the investment"""
