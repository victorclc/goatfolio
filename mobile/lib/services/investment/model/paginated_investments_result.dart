import 'package:goatfolio/services/investment/model/investment.dart';
import 'package:goatfolio/services/investment/model/stock_dividend.dart';
import 'package:goatfolio/services/investment/model/stock_investment.dart';

class PaginatedInvestmentResult {
  String? lastEvaluatedId;
  DateTime? lastEvaluatedDate;
  List<Investment> investments;

  PaginatedInvestmentResult.fromJson(Map<String, dynamic> json)
      : lastEvaluatedId = json["last_evaluated_id"],
        lastEvaluatedDate = json['last_evaluated_date'] != null
            ? DateTime.parse('${json['last_evaluated_date']}')
            : null,
        investments = json["investments"]
            .map<Investment?>(
              (investment) {
                if (investment["type"] == "STOCK") {
                  return StockInvestment.fromJson(investment);
                } else if (investment["type"] == "STOCK_DIVIDEND") {
                  return StockDividend.fromJson(investment);
                }
              },
            )
            .whereType<Investment>()
            .toList();
}
