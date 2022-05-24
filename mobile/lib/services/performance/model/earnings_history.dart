class EarningsDetails {
  final DateTime date;
  final double total;
  final Map<String, double> stocks;

  EarningsDetails.fromJson(Map<String, dynamic> json)
      : date = DateTime.parse(json["date"]),
        total = json["total"],
        stocks = Map<String, double>.from(json["stocks"]);
}

class EarningsHistory {
  List<EarningsDetails> history;
  Map<DateTime, EarningsDetails> map;

  EarningsHistory(this.history) : map = {for (var v in history) v.date: v};

  EarningsHistory.fromJson(List json)
      : history = json
            .map<EarningsDetails>((json) => EarningsDetails.fromJson(json))
            .toList(),
        map = {
          for (var v in json
              .map<EarningsDetails>((json) => EarningsDetails.fromJson(json))
              .toList())
            v.date: v
        };
}
