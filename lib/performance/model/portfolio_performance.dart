
import 'package:goatfolio/performance/model/group_position_summary.dart';
import 'package:goatfolio/performance/model/stock_summary.dart';

class PortfolioPerformance {
  GroupPositionSummary? stockSummary;
  GroupPositionSummary? reitSummary;
  GroupPositionSummary? bdrSummary;

  get grossValue {
    double grossAmount = 0;
    if (stockSummary != null) grossAmount += stockSummary!.grossValue;
    if (reitSummary != null) grossAmount += reitSummary!.grossValue;
    if (bdrSummary != null) grossAmount += bdrSummary!.grossValue;

    return grossAmount;
  }

  List<StockSummary> get allStocks {
    List<StockSummary> stocks = [];
    if (stockSummary != null) stocks += stockSummary!.openedPositions;
    if (reitSummary != null) stocks += reitSummary!.openedPositions;
    if (bdrSummary != null) stocks += bdrSummary!.openedPositions;

    return stocks;
  }

  bool get hasStocks => stockSummary != null;

  bool get hasReits => reitSummary != null;

  bool get hasBdrs => bdrSummary != null;

  PortfolioPerformance.fromJson(Map<String, dynamic> json)
      : stockSummary = json.containsKey('STOCKS')
            ? GroupPositionSummary.fromJson(json['STOCKS'])
            : null,
        reitSummary = json.containsKey('REITS')
            ? GroupPositionSummary.fromJson(json['REITS'])
            : null,
        bdrSummary = json.containsKey('BDRS')
            ? GroupPositionSummary.fromJson(json['BDRS'])
            : null;

  void copy(PortfolioPerformance other) {
    stockSummary = other.stockSummary;
    reitSummary = other.reitSummary;
    bdrSummary = other.bdrSummary;
  }
}
