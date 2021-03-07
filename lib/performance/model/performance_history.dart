class StockPerformanceHistory {
  double monthTotal;
  double rentability;
  DateTime date;

  StockPerformanceHistory.fromJson(Map<String, dynamic> json)
      : monthTotal = json['month_total'],
        rentability = json['rentability'],
        date = DateTime.fromMillisecondsSinceEpoch(json['date'] * 1000);

  @override
  String toString() {
    return 'StockPerformanceHistory{monthTotal: $monthTotal, rentability: $rentability, date: $date}';
  }
}