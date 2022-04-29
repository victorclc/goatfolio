import 'package:goatfolio/services/investment/model/stock.dart';

class PaginatedInvestmentResult {
  String? lastEvaluatedId;
  DateTime? lastEvaluatedDate;
  List<StockInvestment> investments;

  PaginatedInvestmentResult.fromJson(Map<String, dynamic> json)
      : lastEvaluatedId = json["last_evaluated_id"],
        lastEvaluatedDate = json['last_evaluated_date'] != null ? DateTime.parse('${json['last_evaluated_date']}'): null,
        investments = json["investments"]
            .map<StockInvestment>(
                (investment) => StockInvestment.fromJson(investment))
            .toList();
}
