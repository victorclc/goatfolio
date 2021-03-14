import 'package:goatfolio/services/performance/model/portfolio_history.dart';
import 'package:goatfolio/services/performance/model/stock_performance.dart';

class PortfolioPerformance {
  double investedAmount;
  double stockGrossAmount;
  double reitGrossAmount;
  double prevStockGrossAmount;
  double prevReitGrossAmount;
  DateTime initialDate;
  List<StockPerformance> stocks;
  List<StockPerformance> reits;
  List<PortfolioHistory> history;

  get grossAmount => stockGrossAmount + reitGrossAmount;

  get prevDayGrossAmount => prevStockGrossAmount + prevReitGrossAmount;

  get dayVariation => grossAmount - prevDayGrossAmount;

  PortfolioPerformance.fromJson(Map<String, dynamic> json)
      : investedAmount = json['invested_amount'],
        stockGrossAmount = json['stock_gross_amount'],
        reitGrossAmount = json['reit_gross_amount'],
        prevStockGrossAmount = json['stock_prev_gross_amount'],
        prevReitGrossAmount = json['reit_prev_gross_amount'],
        initialDate =
            DateTime.fromMillisecondsSinceEpoch(json['initial_date'] * 1000),
        stocks = json['stocks']
            .map<StockPerformance>((json) => StockPerformance.fromJson(json))
            .toList(),
        history = json['history']
            .map<PortfolioHistory>((json) => PortfolioHistory.fromJson(json))
            .toList()
              ..sort((a, b) => a.date.compareTo(b.date)),
        reits = json['reits']
            .map<StockPerformance>((json) => StockPerformance.fromJson(json))
            .toList();
}
