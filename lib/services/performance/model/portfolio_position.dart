class PortfolioPosition {
  DateTime date;
  double investedValue;
  double grossValue;

  PortfolioPosition.fromJson(Map<String, dynamic> json)
      : date = DateTime.fromMillisecondsSinceEpoch(json['date'] * 1000, isUtc: true),
        investedValue = json['invested_value'],
        grossValue = json['gross_value'];
}
