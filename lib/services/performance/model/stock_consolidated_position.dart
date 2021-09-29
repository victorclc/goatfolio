class StockConsolidatedPosition {
  DateTime date;
  double grossValue;
  double investedValue;
  double variationPerc;

  StockConsolidatedPosition.fromJson(Map<String, dynamic> json)
      : date = DateTime.parse(json['date']),
        grossValue = json['gross_value'],
        investedValue = json['invested_value'],
        variationPerc = json['variation_perc'];
}
