class BenchmarkPosition {
  DateTime date;
  double open;
  double close;

  BenchmarkPosition.fromJson(Map<String, dynamic> json)
      : date = DateTime.fromMillisecondsSinceEpoch(json['date'] * 1000,
      isUtc: true),
        open = json['close'],
        close = json['open'];
}
