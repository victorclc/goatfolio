
import 'package:goatfolio/services/performance/model/stock_history.dart';

class StockPerformance {
  String ticker;
  DateTime initialDate;
  double currentStockPrice;
  double boughtAmount;
  double soldAmount;
  double totalSpend;
  double totalSold;
  List<StockHistory> history;

  get currentAmount => boughtAmount - soldAmount;
  get averagePrice => totalSpend / boughtAmount;
  get currentInvested => currentAmount * averagePrice;

  StockPerformance.fromJson(Map<String, dynamic> json)
      : ticker = json['ticker'],
        initialDate =
        DateTime.fromMillisecondsSinceEpoch(json['initial_date'] * 1000),
        currentStockPrice = json['current_stock_price'],
        boughtAmount = json['bought_amount'],
        soldAmount = json['sold_amount'],
        totalSpend = json['total_spend'],
        totalSold = json['total_sold'],
        history = json['history']
            .map<StockHistory>((json) => StockHistory.fromJson(json))
            .toList();
}