import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class PrettyTextField extends StatelessWidget {
  final TextEditingController? controller;
  final String? label;
  final String? hint;
  final Icon? suffixIcon;
  final bool readOnly;
  final bool upperCaseInput;
  final Function()? onTap;
  final String Function(String?)? validator;
  final Function(String?)? onSaved;
  final TextInputType textInputType;
  final FocusNode? focusNode;
  final bool hideText;
  final String initialText;
  final List<String>? autoFillHints;

  PrettyTextField({
    Key? key,
    this.label,
    this.hint,
    this.suffixIcon,
    this.readOnly = false,
    this.onTap,
    this.controller,
    this.validator,
    this.textInputType = TextInputType.text,
    this.autoFillHints,
    this.onSaved,
    this.upperCaseInput = false,
    this.focusNode,
    this.hideText = false,
    this.initialText = "",
  }) : super(key: key);

  List<TextInputFormatter>? getInputFormatters() {
    if (textInputType == TextInputType.number) {
      return [FilteringTextInputFormatter.digitsOnly];
    } else if (textInputType ==
        TextInputType.numberWithOptions(decimal: true)) {
      // return [
      //   WhitelistingTextInputFormatter.digitsOnly,
      //   CurrencyPtBrInputFormatter(maxDigits: 11),
      // ];
    } else if (upperCaseInput) {
      // return [UpperCaseTextFormatter()];
    }
    return [];
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.only(bottom: 8, top: 8),
      child: TextFormField(
        controller: controller ?? TextEditingController()
          ..text = initialText,
        inputFormatters: getInputFormatters(),
        validator: validator,
        readOnly: readOnly,
        keyboardType: textInputType,
        onTap: onTap,
        onSaved: onSaved,
        focusNode: focusNode,
        obscureText: hideText,
        autofillHints: autoFillHints,
        decoration: new InputDecoration(
          contentPadding: const EdgeInsets.fromLTRB(16, 0, 0, 0),
          border: new OutlineInputBorder(),
          hintText: hint,
          labelText: label,
          prefixText: '',
          suffixIcon: suffixIcon,
        ),
      ),
    );
  }
}
