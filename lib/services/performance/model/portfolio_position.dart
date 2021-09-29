import 'package:intl/intl.dart';

class PortfolioPosition {
  DateTime date;
  double investedValue;
  double grossValue;

  PortfolioPosition.fromJson(Map<String, dynamic> json)
      : date = DateTime.parse(json['date']),
        investedValue = json['invested_value'],
        grossValue = json['gross_value'];
}
