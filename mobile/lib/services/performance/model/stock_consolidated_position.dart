import 'package:goatfolio/services/performance/model/benchmark_position.dart';

class StockConsolidatedPosition {
  DateTime date;
  double grossValue;
  double investedValue;
  double? variationPerc;
  Benchmark benchmark;

  StockConsolidatedPosition.fromJson(Map<String, dynamic> json)
      : date = DateTime.parse(json['date']),
        grossValue = json['gross_value'],
        investedValue = json['invested_value'],
        variationPerc = json['variation_perc'],
        benchmark = Benchmark.fromJson(json['benchmark']);
}
