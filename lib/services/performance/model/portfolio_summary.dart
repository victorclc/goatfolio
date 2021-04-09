import 'package:goatfolio/services/performance/model/stock_variation.dart';

class PortfolioSummary {
  double investedAmount;
  double grossAmount;
  double dayVariation;
  double monthVariation;
  List<StockVariation> stocksVariation;

  PortfolioSummary.fromJson(Map<String, dynamic> json)
      : investedAmount = json['invested_amount'],
        grossAmount = json['gross_amount'],
        dayVariation = json['day_variation'],
        monthVariation = json['month_variation'],
        stocksVariation = json['stocks_variation']
            .map<StockVariation>((json) => StockVariation.fromJson(json))
            .toList();
}
