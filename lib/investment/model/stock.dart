import 'investment.dart';

class StockInvestment extends Investment {
  final String ticker;
  final int amount;
  final double price;

  StockInvestment({
    this.ticker,
    this.amount,
    this.price,
    type,
    operation,
    date,
    id,
    subject,
    broker,
  }) : super(
          type: type,
          operation: operation,
          date: date,
          id: id,
          subject: subject,
          broker: broker,
        );

  StockInvestment.fromJson(Map<String, dynamic> json)
      : ticker = json['ticker'],
        amount = json['amount'].toInt(),
        price = json['price'],
        super.fromJson(json);

  Map<String, dynamic> toJson() => {
        'type': type,
        'operation': operation,
        'ticker': ticker,
        'price': price,
        'amount': amount,
        'date': date,
        'broker': broker,
        'id': id,
        ...super.toJson()
      };
}
