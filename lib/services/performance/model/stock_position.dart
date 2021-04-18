class StockPosition {
  DateTime date;
  double openPrice;
  double closePrice;
  double amount;
  double investedValue;
  double soldValue;

  StockPosition.fromJson(Map<String, dynamic> json)
      : date = DateTime.fromMillisecondsSinceEpoch(json['date'] * 1000, isUtc: true),
        openPrice = json['open_price'],
        closePrice = json['close_price'],
        amount = json['amount'],
        soldValue = json['sold_value'],
        investedValue = json['invested_value'];
}
