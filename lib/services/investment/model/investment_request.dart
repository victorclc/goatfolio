import 'package:goatfolio/services/investment/model/stock.dart';

class InvestmentRequest {
  final String type;
  final StockInvestment investment;

  InvestmentRequest({this.type, this.investment});

  Map<String, dynamic> toJson() => {
        'type': type,
        'investment': investment.toJson(),
      };
}
