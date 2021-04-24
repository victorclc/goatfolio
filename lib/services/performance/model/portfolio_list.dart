import 'package:goatfolio/services/performance/model/stock_summary.dart';

import 'benchmark_position.dart';

class PortfolioList {
  double stockGrossAmount;
  double reitGrossAmount;
  double bdrGrossAmount;
  List<StockSummary> stocks;
  List<StockSummary> reits;
  List<StockSummary> bdrs;
  List<BenchmarkPosition> ibovHistory;

  get grossAmount => stockGrossAmount + reitGrossAmount + bdrGrossAmount;

  PortfolioList.fromJson(Map<String, dynamic> json)
      : stockGrossAmount = json['stock_gross_amount'],
        reitGrossAmount = json['reit_gross_amount'],
        bdrGrossAmount = json['bdr_gross_amount'],
        stocks = json['stocks']
            .map<StockSummary>((json) => StockSummary.fromJson(json))
            .toList(),
        reits = json['reits']
            .map<StockSummary>((json) => StockSummary.fromJson(json))
            .toList(),
        bdrs = json['bdrs']
            .map<StockSummary>((json) => StockSummary.fromJson(json))
            .toList(),
        ibovHistory = json['ibov_history']
            .map<BenchmarkPosition>((json) => BenchmarkPosition.fromJson(json))
            .toList();

  void copy(PortfolioList other) {
    stockGrossAmount = other.stockGrossAmount;
    reitGrossAmount = other.reitGrossAmount;
    bdrGrossAmount = other.bdrGrossAmount;
    stocks = other.stocks;
    reits = other.reits;
    bdrs = other.bdrs;
  }
}
