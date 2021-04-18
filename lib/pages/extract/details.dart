import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/common/formatter/brazil.dart';
import 'package:goatfolio/common/util/dialog.dart';
import 'package:goatfolio/services/investment/model/stock.dart';

import 'package:intl/intl.dart';
import 'package:goatfolio/common/extension/string.dart';

class ExtractDetails extends StatelessWidget {
  final DateFormat formatter = DateFormat('dd MMM yyyy', 'pt_BR');
  final StockInvestment investment;
  final Function onEdited;
  final Function onDeleted;

  ExtractDetails(this.investment, this.onEdited, this.onDeleted, {Key key})
      : super(key: key);

  Widget build(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;
    return CupertinoPageScaffold(
      navigationBar: CupertinoNavigationBar(
        leading: Container(),
        middle: Text("Detalhes"),
        backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
        border: Border(),
        trailing: CupertinoButton(
          padding: EdgeInsets.all(0),
          child: Text('OK'),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      child: SafeArea(
        child: SingleChildScrollView(
          child: Container(
            padding: EdgeInsets.only(top: 16),
            alignment: Alignment.center,
            child: Column(
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    ClipOval(
                      child: Icon(
                        investment.operation == "BUY"
                            ? Icons.trending_up
                            : Icons.trending_down,
                        color: investment.operation == "BUY"
                            ? Colors.green
                            : Colors.red,
                      ),
                    ),
                    SizedBox(
                      height: 24,
                    ),
                    Text(
                      formatter.format(investment.date).capitalizeWords(),
                      style: textTheme.textStyle.copyWith(fontSize: 16),
                    ),
                    Text(
                      investment.broker ?? "",
                      style: textTheme.textStyle.copyWith(fontSize: 16),
                    ),
                    SizedBox(
                      height: 16,
                    ),
                    Text(
                      (investment).ticker.replaceAll('.SA', ''),
                      style: textTheme.textStyle
                          .copyWith(fontSize: 24, fontWeight: FontWeight.w400),
                    ),
                    SizedBox(
                      height: 16,
                    ),
                    Text(
                      moneyFormatter
                          .format((investment).amount * (investment).price),
                      style: textTheme.textStyle
                          .copyWith(fontSize: 24, fontWeight: FontWeight.w600),
                    ),
                    Text(
                      "(${(investment).amount} x ${moneyFormatter.format((investment).price)})",
                      style: textTheme.textStyle.copyWith(fontSize: 14),
                    ),
                    SizedBox(
                      height: 32,
                    ),
                    investment.id.startsWith("CEI")
                        ? Container(
                            padding: EdgeInsets.only(right: 16),
                            alignment: Alignment.topRight,
                            child: Text("*Importado pelo CEI",
                                style:
                                    textTheme.textStyle.copyWith(fontSize: 14)))
                        : Container(),
                  ],
                ),
                SizedBox(
                  height: 40,
                ),
                Padding(
                  padding: const EdgeInsets.all(32.0),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                          child: Padding(
                        padding: const EdgeInsets.only(left: 16, right: 8),
                        child: CupertinoButton.filled(
                          padding: EdgeInsets.zero,
                          child: Text("Editar"),
                          onPressed: () async {
                            await onEdited(investment);
                            Navigator.of(context).pop();
                          },
                        ),
                      )),
                      Expanded(
                          child: Padding(
                        padding: const EdgeInsets.only(left: 8, right: 16),
                        child: CupertinoButton.filled(
                          padding: EdgeInsets.zero,
                          child: Text("Excluir"),
                          onPressed: () async {
                            await DialogUtils.showNoYesDialog(context,
                                title: "Excluir?",
                                message:
                                    "Tem certeza que quer excluir a transação?",
                                onYesPressed: () async {
                              await onDeleted(investment);
                              Navigator.pop(context);
                            });
                          },
                        ),
                      )),
                    ],
                  ),
                )
              ],
            ),
          ),
        ),
      ),
    );
  }
}
