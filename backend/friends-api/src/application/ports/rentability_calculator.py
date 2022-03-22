import abc
from typing import Optional, List, Dict

from application.models.performance import PerformanceSummary


class RentabilityCalculator(abc.ABC):
    @abc.abstractmethod
    def get_performance_for_subjects(self, subjects: List[str]) -> Dict[str, PerformanceSummary]:
        ...
