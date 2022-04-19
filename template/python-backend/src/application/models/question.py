from dataclasses import dataclass
from typing import List


@dataclass
class Question:
    question: str
    answer: str


@dataclass
class Faq:
    topic: str
    description: str
    questions: List[Question]
