class PortfolioHistory {
  DateTime date;
  double totalInvested;
  double grossAmount;

  PortfolioHistory.fromJson(Map<String, dynamic> json)
      : date = DateTime.fromMillisecondsSinceEpoch(json['date'] * 1000),
        totalInvested = json['total_invested'],
        grossAmount = json['gross_amount'];
}
