import 'package:flutter/cupertino.dart';
import 'package:goatfolio/common/widget/multi_prompt.dart';

class CeiTaxIdPrompt extends PromptRequest {
  CeiTaxIdPrompt()
      : super(
          attrName: 'username',
          title: Row(
            children: [
              Text(
                "Qual seu ",
                style: TextStyle(fontSize: 24),
              ),
              Text(
                "CPF",
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
              ),
              Text(
                "?",
                style: TextStyle(fontSize: 24),
              ),
            ],
          ),
          hint: Text(
            "Digite o CPF que deseja realizar a importação.",
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.w200),
          ),
          keyboardType: TextInputType.number,
        );
}

class CeiPasswordPrompt extends PromptRequest {
  CeiPasswordPrompt()
      : super(
            attrName: 'password',
            title: Row(
              children: [
                Text(
                  "Digite sua ",
                  style: TextStyle(fontSize: 24),
                ),
                Text(
                  "senha",
                  style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                ),
                Text(
                  " de acesso ao CEI",
                  style: TextStyle(fontSize: 24),
                ),
              ],
            ),
            hint: Container(),
            keyboardType: TextInputType.visiblePassword,
            autoFillHints: [AutofillHints.password],
            hideText: true);
}
