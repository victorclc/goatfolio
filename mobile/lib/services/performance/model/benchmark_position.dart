class Benchmark {
  String name;
  double open;
  double close;

  Benchmark.fromJson(Map<String, dynamic> json)
      : name = json['name'],
        open = json['open'],
        close = json['close'];
}
