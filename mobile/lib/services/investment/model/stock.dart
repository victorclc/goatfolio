import 'package:intl/intl.dart';

class StockInvestment {
  String type;
  String operation;
  DateTime date;
  String? id;
  String? subject;
  String? broker;
  double costs;
  String ticker;
  int amount;
  double price;
  String? aliasTicker;

  StockInvestment(
      {required this.ticker,
      required this.amount,
      required this.price,
      required this.type,
      required this.operation,
      required this.date,
      this.id,
      this.subject,
      required this.broker,
      required this.costs});

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

  StockInvestment.fromJson(Map<String, dynamic> json)
      : type = json['type'],
        operation = json['operation'],
        date = DateTime.parse('${json['date']}'),
        broker = json['broker'],
        id = json['id'],
        subject = json['subject'],
        ticker = json['ticker'],
        amount = json['amount'].toInt(),
        price = json['price'],
        costs = json['costs'],
        aliasTicker = json['alias_ticker'];

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
