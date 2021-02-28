import 'package:intl/intl.dart';

final NumberFormat moneyFormatter =
new NumberFormat.currency(symbol: "R\$", locale: "pt_BR");
final NumberFormat percentFormatter =
new NumberFormat.decimalPercentPattern(decimalDigits: 2, locale: "pt_BR");

final dateFormatter = DateFormat('yyyy-MM-dd');