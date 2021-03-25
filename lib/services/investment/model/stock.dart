class StockInvestment {
  String type;
  String operation;
  DateTime date;
  String id;
  String subject;
  String broker;
  double costs;
  String ticker;
  int amount;
  double price;

  StockInvestment(
      {this.ticker,
      this.amount,
      this.price,
      this.type,
      this.operation,
      this.date,
      this.id,
      this.subject,
      this.broker,
      this.costs});

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
        'date': date.millisecondsSinceEpoch ~/ 1000,
        'broker': broker,
        'id': id,
        'ticker': ticker,
        'price': price,
        'amount': amount,
        'costs': costs,
      };
}
