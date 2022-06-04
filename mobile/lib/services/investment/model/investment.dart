class Investment {
  String? id;
  String? subject;
  DateTime date;
  String type;

  Investment({
    this.id,
    this.subject,
    required this.date,
    required this.type,
  });

  Investment.fromJson(Map<String, dynamic> json)
      : type = json['type'],
        id = json['type'],
        subject = json['type'],
        date = DateTime.parse('${json['date']}');
}
