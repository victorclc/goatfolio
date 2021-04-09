import 'package:goatfolio/services/performance/model/portfolio_position.dart';
import 'package:goatfolio/services/performance/model/stock_position.dart';

class PortfolioHistory {
  List<PortfolioPosition> history;
  List<StockPosition> ibovHistory;

  PortfolioHistory.fromJson(Map<String, dynamic> json)
      : history = json['history']
            .map<PortfolioPosition>((json) => PortfolioPosition.fromJson(json))
            .toList(),
        ibovHistory = json['ibov_history']
            .map<StockPosition>((json) => StockPosition.fromJson(json))
            .toList();
}
