class Divergence {
  final String ticker;
  final int expectedAmount;
  final int actualAmount;
  final int missingAmount;

  Divergence({
    required this.ticker,
    required this.expectedAmount,
    required this.actualAmount,
    required this.missingAmount,
  });

  Divergence.fromJson(Map<String, dynamic> json)
      : ticker = json['ticker'],
        expectedAmount = json['expected_amount'].toInt(),
        actualAmount = json['actual_amount'].toInt(),
        missingAmount = json['missing_amount'].toInt();
}
