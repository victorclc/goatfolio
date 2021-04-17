class StockSummary {
  String ticker;
  String aliasTicker;
  double amount;
  double averagePrice;
  double investedAmount;
  double currentPrice;
  double grossAmount;

  get currentTickerName =>
      aliasTicker == null || aliasTicker.isEmpty ? ticker : aliasTicker;

  StockSummary.fromJson(Map<String, dynamic> json)
      : ticker = json['ticker'],
        aliasTicker = json['alias_ticker'],
        amount = json['amount'],
        averagePrice = json['average_price'],
        investedAmount = json['invested_amount'],
        currentPrice = json['current_price'],
        grossAmount = json['gross_amount'];
}
