import 'package:intl/intl.dart';

class IncorporationEvent {
  final String ticker;
  final String emittedTicker;
  final double groupingFactor;
  final DateTime lastDatePrior;

  IncorporationEvent({
    required this.ticker,
    required this.emittedTicker,
    required this.groupingFactor,
    required this.lastDatePrior,
  });

  Map<String, dynamic> toJson() => {
        'ticker': ticker,
        'emitted_ticker': emittedTicker,
        'grouping_factor': groupingFactor,
        'last_date_prior': DateFormat("yyyyMMdd").format(lastDatePrior),
      };
}
