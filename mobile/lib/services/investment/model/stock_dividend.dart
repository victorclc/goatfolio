import 'package:goatfolio/services/investment/model/investment.dart';
import 'package:intl/intl.dart';

class StockDividend extends Investment {
  String ticker;
  double amount;
  String label;

  StockDividend({
    required this.ticker,
    required this.amount,
    required this.label,
    required String type,
    required DateTime date,
    String? id,
    String? subject,
  }) : super(id: id, subject: subject, date: date, type: type);

  factory StockDividend.fromJson(Map<String, dynamic> json) => StockDividend(
        type: json['type'],
        date: DateTime.parse('${json['date']}'),
        id: json['id'],
        subject: json['subject'],
        ticker: json['ticker'],
        amount: json['amount'],
        label: json['label'],
      );

  Map<String, dynamic> toJson() => {
        'type': type,
        'date': DateFormat("yyyyMMdd").format(date),
        'id': id,
        'ticker': ticker,
        'amount': amount,
      };
}
