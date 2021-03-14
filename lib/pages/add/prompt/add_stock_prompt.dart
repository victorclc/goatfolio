import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/common/widget/multi_prompt.dart';

class StockTickerPrompt extends PromptRequest {
  StockTickerPrompt()
      : super(
            attrName: 'ticker',
            title: Row(
              children: [
                Text(
                  "Qual o ",
                  style: TextStyle(fontSize: 24),
                ),
                Text(
                  "ticker",
                  style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                ),
                Text(
                  " do ativo?",
                  style: TextStyle(fontSize: 24),
                ),
              ],
            ),
            keyboardType: TextInputType.text);
}

class StockAmountPrompt extends PromptRequest {
  StockAmountPrompt()
      : super(
      attrName: 'amount',
      title: Row(
        children: [
          Text(
            "Quantas ",
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          Text(
            "ações",
            style: TextStyle(fontSize: 24),
          ),
          Text(
            " voce comprou?",
            style: TextStyle(fontSize: 24),
          ),
        ],
      ),
      keyboardType: TextInputType.text);
}

class StockPricePrompt extends PromptRequest {
  StockPricePrompt()
      : super(
      attrName: 'price',
      title: Row(
        children: [
          Text(
            "Qual o ",
            style: TextStyle(fontSize: 24),
          ),
          Text(
            "preço",
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          Text(
            " que voce pagou?",
            style: TextStyle(fontSize: 24),
          ),
        ],
      ),
      keyboardType: TextInputType.text);
}

class StockDatePrompt extends PromptRequest {
  StockDatePrompt()
      : super(
      attrName: 'data',
      title: Row(
        children: [
          Text(
            "Quando ",
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          Text(
            "voce comprou o ativo?",
            style: TextStyle(fontSize: 24),
          ),
        ],
      ),
      keyboardType: TextInputType.text);
}

class StockCostsPrompt extends PromptRequest {
  StockCostsPrompt()
      : super(
      attrName: 'costs',
      title: Row(
        children: [
          Text(
            "Qual o ",
            style: TextStyle(fontSize: 24),
          ),
          Text(
            "custo",
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          Text(
            "da operação?",
            style: TextStyle(fontSize: 24),
          ),
        ],
      ),
      hint: Text(
        "Taxas de corretagem, etc",
        style: TextStyle(fontSize: 16, fontWeight: FontWeight.w200),
      ),
      keyboardType: TextInputType.text);
}

class StockBrokerPrompt extends PromptRequest {
  StockBrokerPrompt()
      : super(
      attrName: 'broker',
      title: Row(
        children: [
          Text(
            "Em qual ",
            style: TextStyle(fontSize: 24),
          ),
          Text(
            "corretora/banco",
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          Text(
            " voce fez essa operação?",
            style: TextStyle(fontSize: 24),
          ),
        ],
      ),
      keyboardType: TextInputType.text);
}
