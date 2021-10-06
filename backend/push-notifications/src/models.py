from dataclasses import dataclass, field
from typing import List


@dataclass
class UserTokens:
    subject: str
    tokens: List = field(default_factory=list)
