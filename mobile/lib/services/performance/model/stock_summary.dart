class StockSummary {
  String ticker;
  String? aliasTicker;
  double quantity;
  double averagePrice;
  double investedValue;
  double lastPrice;

  get grossValue => quantity * lastPrice;

  get currentTickerName =>
      aliasTicker == null || aliasTicker!.isEmpty ? ticker : aliasTicker;

  StockSummary.fromJson(Map<String, dynamic> json)
      : ticker = json['ticker'],
        aliasTicker = json['alias_ticker'],
        quantity = json['quantity'],
        averagePrice = json['average_price'],
        investedValue = json['invested_value'],
        lastPrice = json['last_price'];
}
