import 'package:goatfolio/investment/model/stock.dart';

class InvestmentRequest {
  final String type;
  final StockInvestment investment;

  InvestmentRequest({required this.type, required this.investment});

  Map<String, dynamic> toJson() => {
        'type': type,
        'investment': investment.toJson(),
      };
}
