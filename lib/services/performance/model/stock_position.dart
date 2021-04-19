class StockPosition {
  DateTime date;
  double openPrice;
  double closePrice;
  double amount;
  double investedValue;
  double soldValue;
  double soldAmount;
  double boughtAmount;
  double realizedProfit;

  StockPosition.fromJson(Map<String, dynamic> json)
      : date = DateTime.fromMillisecondsSinceEpoch(json['date'] * 1000,
            isUtc: true),
        openPrice = json['open_price'],
        closePrice = json['close_price'],
        amount = json['amount'],
        soldValue = json['sold_value'],
        soldAmount = json['sold_amount'],
        boughtAmount = json['bought_amount'],
        realizedProfit = json['realized_profit'],
        investedValue = json['invested_value'];
}
