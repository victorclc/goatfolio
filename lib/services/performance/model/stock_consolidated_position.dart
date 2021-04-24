class StockConsolidatedPosition {
  DateTime date;
  double grossValue;
  double investedValue;
  double variationPerc;

  StockConsolidatedPosition.fromJson(Map<String, dynamic> json)
      : date = DateTime.fromMillisecondsSinceEpoch(json['date'] * 1000,
            isUtc: true),
        grossValue = json['gross_value'],
        investedValue = json['invested_value'],
        variationPerc = json['variation_perc'];
}
