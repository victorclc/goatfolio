class StockPosition {
  double boughtAmount;
  double soldAmount;
  double totalSpend;
  double totalSold;
  double averagePrice;
  double currentAmount;
  double currentInvested;

  StockPosition({
    this.boughtAmount,
    this.soldAmount,
    this.totalSpend,
    this.totalSold,
    this.averagePrice,
    this.currentAmount,
    this.currentInvested,
  });

  StockPosition.fromJson(Map<String, dynamic> json)
      : boughtAmount = json['bought_amount'],
        soldAmount = json['sold_amount'],
        totalSpend = json['total_spend'],
        totalSold = json['total_sold'],
        averagePrice = json['average_price'],
        currentAmount = json['current_amount'],
        currentInvested = json['current_invested'];
}
