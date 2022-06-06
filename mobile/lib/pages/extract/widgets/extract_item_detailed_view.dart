import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/services/investment/model/paginated_extract_result.dart';
import 'package:goatfolio/utils/dialog.dart' as dialog;
import 'package:goatfolio/utils/extensions.dart';
import 'package:intl/intl.dart';

class ExtractItemDetailedView extends StatelessWidget {
  final DateFormat formatter = DateFormat('dd MMM yyyy', 'pt_BR');
  final ExtractItem item;
  final Function onEdited;
  final Function onDeleted;

  ExtractItemDetailedView(this.item, this.onEdited, this.onDeleted, {Key? key})
      : super(key: key);

  bool isModifiable() {
    return item.modifiable;
  }

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
                      child: item.icon.iconWidget,
                    ),
                    SizedBox(
                      height: 24,
                    ),
                    Text(
                      formatter.format(item.date).capitalizeWords(),
                      style: textTheme.textStyle.copyWith(fontSize: 16),
                    ),
                    Text(
                      item.additionalInfo1,
                      style: textTheme.textStyle.copyWith(fontSize: 16),
                    ),
                    SizedBox(
                      height: 16,
                    ),
                    Text(
                      item.key,
                      style: textTheme.textStyle
                          .copyWith(fontSize: 24, fontWeight: FontWeight.w400),
                    ),
                    SizedBox(
                      height: 16,
                    ),
                    Text(
                      item.value,
                      style: textTheme.textStyle
                          .copyWith(fontSize: 24, fontWeight: FontWeight.w600),
                    ),
                    Text(
                      item.additionalInfo2,
                      style: textTheme.textStyle.copyWith(fontSize: 14),
                    ),
                    SizedBox(
                      height: 32,
                    ),
                    Container(
                        padding: EdgeInsets.only(right: 16),
                        alignment: Alignment.topRight,
                        child: Text(item.observation,
                            style: textTheme.textStyle.copyWith(fontSize: 14)))
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
                          onPressed: isModifiable()
                              ? () async {
                                  await onEdited(item.investment);
                                  Navigator.of(context).pop();
                                }
                              : null,
                        ),
                      )),
                      Expanded(
                          child: Padding(
                        padding: const EdgeInsets.only(left: 8, right: 16),
                        child: CupertinoButton.filled(
                          padding: EdgeInsets.zero,
                          child: Text("Excluir"),
                          onPressed: isModifiable()
                              ? () async {
                                  await dialog.showNoYesDialog(context,
                                      title: "Excluir?",
                                      message:
                                          "Tem certeza que quer excluir a transação?",
                                      onYesPressed: () async {
                                    await onDeleted(item);
                                    Navigator.pop(context);
                                  });
                                }
                              : null,
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
