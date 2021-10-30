
import 'package:goatfolio/services/performance/model/stock_consolidated_position.dart';

class TickerConsolidatedHistory {
  List<StockConsolidatedPosition> history;

  TickerConsolidatedHistory.fromJson(Map<String, dynamic> json)
      : history = json['history']
            .map<StockConsolidatedPosition>(
                (json) => StockConsolidatedPosition.fromJson(json))
            .toList();
}
