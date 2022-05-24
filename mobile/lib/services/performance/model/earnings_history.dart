class EarningsDetails {
  final DateTime date;
  final Map<String, double> stocks;

  EarningsDetails.fromJson(Map<String, dynamic> json)
      : date = DateTime.parse(json["date"]),
        stocks = Map<String, double>.from(json["stocks"]);
}

class EarningsHistory {
  List<EarningsDetails> history;


  EarningsHistory(this.history);

  EarningsHistory.fromJson(List json)
      : history = json
            .map<EarningsDetails>((json) => EarningsDetails.fromJson(json))
            .toList();
}
