class PortfolioPosition {
  DateTime date;
  double totalInvested;
  double grossAmount;

  PortfolioPosition.fromJson(Map<String, dynamic> json)
      : date = DateTime.fromMillisecondsSinceEpoch(json['date'] * 1000),
        totalInvested = json['total_invested'],
        grossAmount = json['gross_amount'];
}
