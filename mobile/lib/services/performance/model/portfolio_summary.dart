

import 'package:goatfolio/services/performance/model/stock_variation.dart';

class PortfolioSummary {
  double investedAmount;
  double grossAmount;
  double dayVariation;
  double monthVariation;
  List<StockVariation> tickerVariation;

  PortfolioSummary.fromJson(Map<String, dynamic> json)
      : investedAmount = json['invested_amount'],
        grossAmount = json['gross_amount'],
        dayVariation = json['day_variation'],
        monthVariation = json['month_variation'],
        tickerVariation = json['ticker_variation']
            .map<StockVariation>((json) => StockVariation.fromJson(json))
            .toList();

  void copy(PortfolioSummary other) {
    investedAmount = other.investedAmount;
    grossAmount = other.grossAmount;
    dayVariation = other.dayVariation;
    monthVariation = other.monthVariation;
    tickerVariation = other.tickerVariation;
  }
}
