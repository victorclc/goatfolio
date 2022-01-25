from dataclasses import dataclass
from typing import List


@dataclass
class Question:
    question: str
    answer: str


@dataclass
class Faq:
    topic: str
    questions: List[Question]
