class Investment {
  final String type;
  final String operation;
  final DateTime date;
  final String id;
  final String subject;
  final String broker;
  final double costs = null;

  Investment(
      {this.type,
        this.operation,
        this.date,
        this.id,
        this.subject,
        this.broker});

  Investment.fromJson(Map<String, dynamic> json)
      : type = json['type'],
        operation = json['operation'],
        date = DateTime.fromMillisecondsSinceEpoch(json['date'] * 1000),
        id = json['id'],
        subject = json['subject'],
        broker = json['broker'];

  Map<String, dynamic> toJson() => {
    'type': type,
    'operation': operation,
    'date': date.millisecondsSinceEpoch * 1000,
    'broker': broker,
    'id': id,
  };
}