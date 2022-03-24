from typing import List, Callable, Dict, Set

from domain.performance.performance import PerformanceSummary, PerformancePercentageSummary

PerformanceSummaryCalculator = Callable[[str], PerformanceSummary]


def get_performance_summary_for_subjects(subjects: Set[str], calculator: PerformanceSummaryCalculator) \
        -> Dict[str, PerformancePercentageSummary]:
    summaries = {}
    for subject in subjects:
        summaries[subject] = calculator(subject).to_percentage_summary()

    return summaries
