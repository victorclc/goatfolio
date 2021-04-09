import 'package:goatfolio/services/performance/model/stock_position.dart';

class TickerConsolidatedHistory {
  List<StockPosition> history;

  TickerConsolidatedHistory.fromJson(Map<String, dynamic> json)
      : history = json['history']
            .map<StockPosition>((json) => StockPosition.fromJson(json))
            .toList();
}
