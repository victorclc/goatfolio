import os
from typing import List, Dict

import requests

from application.models.performance import PerformancePercentageSummary
from application.ports.rentability_calculator import RentabilityCalculator
from goatcommons.configuration.system_manager import ConfigurationClient
from goatcommons.utils import json as jsonutils


class RESTRentabilityCalculator(RentabilityCalculator):
    def __init__(self):
        self._RENTABILITY_URL = os.getenv("RENTABILITY_BASE_API_URL")
        self.__api_key = ConfigurationClient().get_secret("portfolio-api-key")

    def get_performance_for_subjects(self, subjects: List[str]) -> Dict[str, PerformancePercentageSummary]:
        response = requests.post(f"{self._RENTABILITY_URL}/summaries", headers={"x-api-key": self.__api_key},
                                 data=jsonutils.dump({"subjects": subjects}))
        performance_raw: Dict = response.json()

        return {k: PerformancePercentageSummary(**v) for k, v in performance_raw.items()}


if __name__ == '__main__':
    print(RESTRentabilityCalculator().get_performance_for_subjects(["41e4a793-3ef5-4413-82e2-80919bce7c1a"]))
