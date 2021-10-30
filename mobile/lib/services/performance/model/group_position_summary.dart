

import 'package:goatfolio/services/performance/model/stock_summary.dart';

class GroupPositionSummary {
  double grossValue;
  List<StockSummary> openedPositions;

  GroupPositionSummary.fromJson(Map<String, dynamic> json)
      : grossValue = json['gross_value'],
        openedPositions = json['opened_positions']
            .map<StockSummary>((json) => StockSummary.fromJson(json))
            .toList();
}
