import 'package:goatfolio/services/performance/model/portfolio_position.dart';
import 'package:goatfolio/services/performance/model/stock_position.dart';
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
  List<PortfolioPosition> history;
  List<StockPosition> ibovHistory;

  get grossAmount => stockGrossAmount + reitGrossAmount;

  get result => grossAmount - investedAmount;

  get prevDayGrossAmount => prevStockGrossAmount + prevReitGrossAmount;

  get dayVariation => grossAmount - prevDayGrossAmount;

  PortfolioPerformance.fromJson(Map<String, dynamic> json)
      : investedAmount = json['invested_amount'],
        stockGrossAmount = json['stock_gross_amount'],
        reitGrossAmount = json['reit_gross_amount'],
        prevStockGrossAmount = json['stock_prev_gross_amount'],
        prevReitGrossAmount = json['reit_prev_gross_amount'],
        initialDate =
            DateTime.fromMillisecondsSinceEpoch(json['initial_date'] * 1000, isUtc: true),
        stocks = json['stocks']
            .map<StockPerformance>((json) => StockPerformance.fromJson(json))
            .toList(),
        history = json['history']
            .map<PortfolioPosition>((json) => PortfolioPosition.fromJson(json))
            .toList(),
        ibovHistory = json['ibov_history']
            .map<StockPosition>((json) => StockPosition.fromJson(json))
            .toList(),
        reits = json['reits']
            .map<StockPerformance>((json) => StockPerformance.fromJson(json))
            .toList();
}
