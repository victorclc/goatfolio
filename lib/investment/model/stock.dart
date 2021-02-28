class StockInvestment {
  final String type;
  final String operation;
  final DateTime date;
  final String id;
  final String subject;
  final String broker;
  final double costs;
  final String ticker;
  final int amount;
  final double price;

  StockInvestment({
    this.ticker,
    this.amount,
    this.price,
    this.type,
    this.operation,
    this.date,
    this.id,
    this.subject,
    this.broker,
    this.costs
  });

  StockInvestment.fromJson(Map<String, dynamic> json)
      : type = json['type'],
        operation = json['operation'],
        date = DateTime.fromMillisecondsSinceEpoch(json['date'] * 1000),
        broker = json['broker'],
        id = json['id'],
        subject = json['subject'],
        ticker = json['ticker'],
        amount = json['amount'].toInt(),
        price = json['price'],
        costs = json['costs'];

  Map<String, dynamic> toJson() => {
        'type': type,
        'operation': operation,
        'date': date.millisecondsSinceEpoch * 1000,
        'broker': broker,
        'id': id,
        'ticker': ticker,
        'price': price,
        'amount': amount,
        'costs': costs,
      };
}
