class Divergence {
  final String ticker;
  final int expectedAmount;
  final int actualAmount;

  Divergence({
    required this.ticker,
    required this.expectedAmount,
    required this.actualAmount,
  });

  get missingAmount => expectedAmount - actualAmount;

  Divergence.fromJson(Map<String, dynamic> json)
      : ticker = json['ticker'],
        expectedAmount = json['expected_amount'].toInt(),
        actualAmount = json['actual_amount'].toInt();
}
