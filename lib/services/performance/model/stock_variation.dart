class StockVariation {
  String ticker;
  double variation;
  double lastPrice;

  StockVariation.fromJson(Map<String, dynamic> json)
      : ticker = json['ticker'],
        variation = json['variation'],
        lastPrice = json['last_price'];
}
