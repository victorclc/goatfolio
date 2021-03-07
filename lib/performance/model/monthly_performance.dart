import 'package:goatfolio/performance/model/performance_history.dart';
import 'package:goatfolio/performance/model/position.dart';

class StockMonthlyPerformance {
  String ticker;
  DateTime initialDate;
  StockPosition position;
  List<StockPerformanceHistory> performanceHistory;

  StockMonthlyPerformance.fromJson(Map<String, dynamic> json)
      : ticker = json['ticker'],
        initialDate =
            DateTime.fromMillisecondsSinceEpoch(json['initial_date'] * 1000),
        position = StockPosition.fromJson(json['position']),
        performanceHistory = json['performance_history']
            .map<StockPerformanceHistory>(
                (json) => StockPerformanceHistory.fromJson(json))
            .toList();

  @override
  String toString() {
    return 'StockMonthlyPerformance{ticker: $ticker, initialDate: $initialDate, position: $position, performanceHistory: $performanceHistory}';
  }
}
