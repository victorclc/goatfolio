
import 'package:goatfolio/services/investment/model/stock_investment.dart';

class InvestmentRequest {
  final String type;
  final StockInvestment investment;

  InvestmentRequest({required this.type, required this.investment});

  Map<String, dynamic> toJson() => {
        'type': type,
        'investment': investment.toJson(),
      };
}
