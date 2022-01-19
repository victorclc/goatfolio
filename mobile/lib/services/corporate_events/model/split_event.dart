import 'package:intl/intl.dart';

class SplitEvent {
  final String ticker;
  final double groupingFactor;
  final DateTime lastDatePrior;

  SplitEvent({
    required this.ticker,
    required this.groupingFactor,
    required this.lastDatePrior,
  });

  Map<String, dynamic> toJson() => {
    'ticker': ticker,
    'grouping_factor': groupingFactor,
    'last_date_prior': DateFormat("yyyyMMdd").format(lastDatePrior),
  };
}
