
import 'package:goatfolio/services/performance/model/portfolio_position.dart';

class PortfolioHistory {
  List<PortfolioPosition> history;

  PortfolioHistory.fromJson(List json)
      : history = json
            .map<PortfolioPosition>((json) => PortfolioPosition.fromJson(json))
            .toList();
}
