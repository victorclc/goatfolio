
import 'package:goatfolio/services/performance/model/stock_position.dart';

class StockPerformance {
  String ticker;
  DateTime initialDate;
  double currentStockPrice;
  double boughtAmount;
  double soldAmount;
  double totalSpend;
  double totalSold;
  double currentDayChangePercent;
  List<StockPosition> history;

  get currentAmount => boughtAmount - soldAmount;
  get averagePrice => totalSpend / boughtAmount;
  get currentInvested => currentAmount * averagePrice;

  StockPerformance.fromJson(Map<String, dynamic> json)
      : ticker = json['ticker'],
        initialDate =
        DateTime.fromMillisecondsSinceEpoch(json['initial_date'] * 1000, isUtc: true),
        currentStockPrice = json['current_stock_price'],
        boughtAmount = json['bought_amount'],
        soldAmount = json['sold_amount'],
        totalSpend = json['total_spend'],
        totalSold = json['total_sold'],
        currentDayChangePercent = json['current_day_change_percent'],
        history = json['history']
            .map<StockPosition>((json) => StockPosition.fromJson(json))
            .toList();
}