import 'package:goatfolio/performance/model/stock_performance.dart';

class PortfolioPerformance {
  double investedAmount;
  double stockGrossAmount;
  double reitGrossAmount;
  DateTime initialDate;
  List<StockPerformance> stocks;
  List<StockPerformance> reits;

  get grossAmount => stockGrossAmount + reitGrossAmount;

  PortfolioPerformance.fromJson(Map<String, dynamic> json)
      : investedAmount = json['invested_amount'],
        stockGrossAmount = json['stock_gross_amount'],
        reitGrossAmount = json['reit_gross_amount'],
        initialDate =
            DateTime.fromMillisecondsSinceEpoch(json['initial_date'] * 1000),
        stocks = json['stocks']
            .map<StockPerformance>((json) => StockPerformance.fromJson(json))
            .toList(),
        reits = json['reits']
            .map<StockPerformance>((json) => StockPerformance.fromJson(json))
            .toList();
}
