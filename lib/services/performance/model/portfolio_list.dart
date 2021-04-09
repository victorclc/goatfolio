import 'package:goatfolio/services/performance/model/stock_position.dart';
import 'package:goatfolio/services/performance/model/stock_summary.dart';

class PortfolioList {
  double stockGrossAmount;
  double reitGrossAmount;
  double bdrGrossAmount;
  List<StockSummary> stocks;
  List<StockSummary> reits;
  List<StockSummary> bdrs;

  get grossAmount => stockGrossAmount + reitGrossAmount + bdrGrossAmount;

  get ibovHistory {
    List<StockPosition> ibov = [];
    return ibov;
  }

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
            .toList();
}
