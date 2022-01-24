import 'package:flutter/cupertino.dart';
import 'package:flutter/services.dart';
import 'package:intl/intl.dart';
import 'package:mask_text_input_formatter/mask_text_input_formatter.dart';

final NumberFormat moneyFormatter =
    new NumberFormat.currency(symbol: "R\$", locale: "pt_BR");
final NumberFormat percentFormatter =
    new NumberFormat.decimalPercentPattern(decimalDigits: 2, locale: "pt_BR");

final dateFormatter = DateFormat('yyyy-MM-dd');

class CurrencyPtBrInputFormatter extends TextInputFormatter {
  CurrencyPtBrInputFormatter();


  String format(String text) {
    final formatter = new NumberFormat("#,##0.00", "pt_BR");
    double value = double.parse(text.replaceAllMapped(RegExp(r'\D'), (match) {
      return '';
    }));
    return "R\$ " + formatter.format(value / 100);
  }

  TextEditingValue formatEditUpdate(
      TextEditingValue oldValue, TextEditingValue newValue) {
    if (newValue.selection.baseOffset == 0) {
      return newValue;
    }

    String newText = format(newValue.text);
    return newValue.copyWith(
        text: newText,
        selection: new TextSelection.collapsed(offset: newText.length));
  }
}

class UpperCaseTextFormatter extends TextInputFormatter {
  @override
  TextEditingValue formatEditUpdate(
      TextEditingValue oldValue, TextEditingValue newValue) {
    return TextEditingValue(
      text: newValue.text.toUpperCase(),
      selection: newValue.selection,
    );
  }
}

final cpfInputFormatter = new MaskTextInputFormatter(
    mask: '###.###.###-##', filter: {"#": RegExp(r'[0-9]')});
final moneyInputFormatter = CurrencyPtBrInputFormatter();
final dateInputFormatter = new MaskTextInputFormatter(
    mask: '##/##/####', filter: {"#": RegExp(r'[0-9]')});

final numberInputFormatter = new MaskTextInputFormatter(
    mask: '##########', filter: {"#": RegExp(r'[0-9]')});
