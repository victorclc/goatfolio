import 'package:flutter/services.dart';
import 'package:intl/intl.dart';
import 'package:mask_text_input_formatter/mask_text_input_formatter.dart';

final NumberFormat moneyFormatter =
new NumberFormat.currency(symbol: "R\$", locale: "pt_BR");
final NumberFormat percentFormatter =
new NumberFormat.decimalPercentPattern(decimalDigits: 2, locale: "pt_BR");

final dateFormatter = DateFormat('yyyy-MM-dd');

class CurrencyPtBrInputFormatter extends TextInputFormatter {
  CurrencyPtBrInputFormatter({this.maxDigits});

  final int maxDigits;

  TextEditingValue formatEditUpdate(
      TextEditingValue oldValue, TextEditingValue newValue) {
    if (newValue.selection.baseOffset == 0) {
      return newValue;
    }

    if (maxDigits != null && newValue.selection.baseOffset > maxDigits) {
      return oldValue;
    }

    double value = double.parse(newValue.text);
    final formatter = new NumberFormat("#,##0.00", "pt_BR");
    String newText = "R\$ " + formatter.format(value / 100);
    return newValue.copyWith(
        text: newText,
        selection: new TextSelection.collapsed(offset: newText.length));
  }
}

final cpfInputFormatter = new MaskTextInputFormatter(mask: '###.###.###-##', filter: { "#": RegExp(r'[0-9]') });
final moneyInputFormatter = new MaskTextInputFormatter(mask: 'R\$ #,##0.00', filter: { "#": RegExp(r'[0-9]') });
final dateInputFormatter = new MaskTextInputFormatter(mask: '##/##/####', filter: { "#": RegExp(r'[0-9]') });