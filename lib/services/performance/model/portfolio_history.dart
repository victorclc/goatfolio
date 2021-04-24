import 'package:goatfolio/services/performance/model/portfolio_position.dart';

import 'benchmark_position.dart';

class PortfolioHistory {
  List<PortfolioPosition> history;
  List<BenchmarkPosition> ibovHistory;

  PortfolioHistory.fromJson(Map<String, dynamic> json)
      : history = json['history']
            .map<PortfolioPosition>((json) => PortfolioPosition.fromJson(json))
            .toList(),
        ibovHistory = json['ibov_history']
            .map<BenchmarkPosition>((json) => BenchmarkPosition.fromJson(json))
            .toList();
}
