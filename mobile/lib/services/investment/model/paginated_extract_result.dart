import 'package:flutter/cupertino.dart';
import 'package:goatfolio/services/investment/model/investment.dart';
import 'package:goatfolio/services/investment/model/stock_dividend.dart';
import 'package:goatfolio/services/investment/model/stock_investment.dart';

Investment? parseInvestment(Map<String, dynamic> investment) {
  if (investment["type"] == "STOCK") {
    return StockInvestment.fromJson(investment);
  } else if (investment["type"] == "STOCK_DIVIDEND") {
    return StockDividend.fromJson(investment);
  }
}

class ExtractIcon {
  int color;
  int codePoint;

  ExtractIcon(this.color, this.codePoint);

  ExtractIcon.fromJson(Map<String, dynamic> json)
      : color = json["color"],
        codePoint = json["code_point"];

  get iconWidget => Icon(
        IconData(
          codePoint,
          fontFamily: "MaterialIcons",
          matchTextDirection: true,
        ),
        color: Color(color),
      );
}

class ExtractItem {
  ExtractIcon icon;
  DateTime date;
  String key;
  String value;
  String label;
  String additionalInfo1;
  String additionalInfo2;
  String observation;
  bool modifiable;
  Investment? investment;

  ExtractItem.fromJson(Map<String, dynamic> json)
      : icon = ExtractIcon.fromJson(json["icon"]),
        date = DateTime.parse(json["date"]),
        key = json["key"],
        value = json["value"],
        label = json["label"],
        additionalInfo1 = json["additional_info_1"],
        additionalInfo2 = json["additional_info_2"],
        observation = json["observation"],
        modifiable = json["modifiable"],
        investment = parseInvestment(json["investment"]);
}

class PaginatedExtractResult {
  String? lastEvaluatedId;
  DateTime? lastEvaluatedDate;
  List<ExtractItem> items;

  PaginatedExtractResult.fromJson(Map<String, dynamic> json)
      : lastEvaluatedId = json["last_evaluated_id"],
        lastEvaluatedDate = json['last_evaluated_date'] != null
            ? DateTime.parse('${json['last_evaluated_date']}')
            : null,
        items = json["items"]
            .map<ExtractItem>((item) => ExtractItem.fromJson(item))
            .toList();
}
