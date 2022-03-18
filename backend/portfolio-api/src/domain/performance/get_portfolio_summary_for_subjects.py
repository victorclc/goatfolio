from typing import List, Callable, Dict, Set

from domain.performance.performance import PerformanceSummary

PerformanceSummaryCalculator = Callable[[str], PerformanceSummary]


def get_performance_summary_for_subjects(subjects: Set[str], calculator: PerformanceSummaryCalculator) \
        -> Dict[str, PerformanceSummary]:
    summaries = {}
    for subject in subjects:
        summaries[subject] = calculator(subject)

    return summaries
