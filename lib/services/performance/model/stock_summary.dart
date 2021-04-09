class StockSummary {
  String ticker;
  double amount;
  double averagePrice;
  double investedAmount;
  double currentPrice;
  double grossAmount;

  StockSummary.fromJson(Map<String, dynamic> json)
      : ticker = json['ticker'],
        amount = json['amount'],
        averagePrice = json['average_price'],
        investedAmount = json['invested_amount'],
        currentPrice = json['current_price'],
        grossAmount = json['gross_amount'];
}