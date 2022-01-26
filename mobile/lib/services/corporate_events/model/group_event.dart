import 'package:intl/intl.dart';

class GroupEvent {
  final String ticker;
  final double groupingFactor;
  final DateTime lastDatePrior;

  GroupEvent({
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
