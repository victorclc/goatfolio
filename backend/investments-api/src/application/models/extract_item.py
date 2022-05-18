import datetime
from dataclasses import dataclass

from application.investment import Investment
from application.models.extract_icon import ExtractIcon


@dataclass
class ExtractItem:
    icon: ExtractIcon
    label: str
    date: datetime.date
    key: str
    value: str
    additional_info_1: str
    additional_info_2: str
    observation: str
    modifiable: bool
    investment: Investment

    def to_json(self):
        return {
            **self.__dict__,
            "icon": self.icon.to_json(),
            "date": self.date.strftime("%Y%m%d"),
            "investment": self.investment.to_json()
        }
