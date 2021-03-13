import 'package:goatfolio/performance/model/stock_performance.dart';

class PortfolioPerformance {
  double investedAmount;
  double grossAmount;
  DateTime initialDate;
  List<StockPerformance> stocks;

  PortfolioPerformance.fromJson(Map<String, dynamic> json)
      : investedAmount = json['invested_amount'],
        grossAmount = json['gross_amount'],
        initialDate =
            DateTime.fromMillisecondsSinceEpoch(json['initial_date'] * 1000),
        stocks = json['stocks']
            .map<StockPerformance>((json) => StockPerformance.fromJson(json))
            .toList();
}
