import 'package:goatfolio/services/investment/model/investment.dart';
import 'package:intl/intl.dart';

class StockInvestment extends Investment {
  String operation;
  String? broker;
  double costs;
  String ticker;
  int amount;
  double price;
  String? aliasTicker;

  StockInvestment({
    required this.ticker,
    required this.amount,
    required this.price,
    required String type,
    required this.operation,
    required DateTime date,
    String? id,
    String? subject,
    required this.broker,
    required this.costs,
    this.aliasTicker
  }): super(id: id, subject: subject, date: date, type: type);

  void copy(StockInvestment inv) {
    this.ticker = inv.ticker;
    this.amount = inv.amount;
    this.price = inv.price;
    this.type = inv.type;
    this.operation = inv.operation;
    this.date = inv.date;
    this.id = inv.id;
    this.subject = inv.subject;
    this.broker = inv.broker;
    this.costs = inv.costs;
  }

  factory StockInvestment.fromJson(Map<String, dynamic> json) => StockInvestment(
      operation: json['operation'],
      type: json['type'],
      date: DateTime.parse('${json['date']}'),
      id: json['id'],
      subject: json['subject'],
      broker: json['broker'],
      ticker: json['ticker'],
      amount: json['amount'].toInt(),
      price: json['price'],
      costs: json['costs'],
      aliasTicker: json['alias_ticker']
  );

  Map<String, dynamic> toJson() => {
        'type': type,
        'operation': operation,
        'date': DateFormat("yyyyMMdd").format(date),
        'broker': broker,
        'id': id,
        'ticker': ticker,
        'price': price,
        'amount': amount,
        'costs': costs,
        'alias_ticker': aliasTicker
      };
}
