class StockPosition {
  DateTime date;
  double openPrice;
  double closePrice;
  double amount;
  double investedAmount;

  StockPosition.fromJson(Map<String, dynamic> json)
      : date = DateTime.fromMillisecondsSinceEpoch(json['date'] * 1000),
        openPrice = json['open_price'],
        closePrice = json['close_price'],
        amount = json['amount'],
        investedAmount = json['invested_amount'];
}
