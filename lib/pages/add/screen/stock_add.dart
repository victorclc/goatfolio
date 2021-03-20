import 'package:flutter/cupertino.dart';
import 'package:goatfolio/common/formatter/brazil.dart';
import 'package:goatfolio/common/util/dialog.dart';
import 'package:goatfolio/common/util/modal.dart';
import 'package:goatfolio/common/widget/progress_indicator_scaffold.dart';

class StockAdd extends StatefulWidget {

  @override
  _StockAddState createState() => _StockAddState();
}

class _StockAddState extends State<StockAdd> {
  final TextEditingController _tickerController = TextEditingController();
  final TextEditingController _brokerController = TextEditingController();
  final TextEditingController _amountController = TextEditingController();
  final TextEditingController _priceController = TextEditingController();
  final TextEditingController _dateController = TextEditingController();
  final TextEditingController _costsController = TextEditingController();
  Future _future;

  bool canSubmit() {
    return _tickerController.text.isNotEmpty &&
        _brokerController.text.isNotEmpty &&
        _amountController.text.isNotEmpty &&
        _priceController.text.isNotEmpty &&
        _dateController.text.isNotEmpty;
  }

  Future<void> submitRequest() async {
    return;
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;
    return CupertinoPageScaffold(
        navigationBar: CupertinoNavigationBar(
          border: null,
          backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
          leading: CupertinoButton(
            padding: EdgeInsets.all(0),
            child: Align(
              alignment: AlignmentDirectional.centerStart,
              widthFactor: 1.0,
              child: Text(
                'Cancelar',
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ),
            onPressed: () => Navigator.of(context).pop(),
          ),
          middle: Text(
            'Nova compra',
            style: textTheme.navTitleTextStyle,
          ),
          trailing: CupertinoButton(
            padding: EdgeInsets.all(0),
            child: Align(
              alignment: AlignmentDirectional.centerStart,
              widthFactor: 1.0,
              child: Text(
                'Seguinte',
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ),
            onPressed: canSubmit()
                ? () => ModalUtils.showUnDismissibleModalBottomSheet(
                      context,
                      ProgressIndicatorScaffold(
                          message: 'Solicitando importação...',
                          future: submitRequest(),
                          onFinish: () async {
                            try {
                              await _future;
                              await DialogUtils.showSuccessDialog(context,
                                  "Importação solicitada com sucesso!");
                            } catch (Exceptions) {
                              await DialogUtils.showErrorDialog(context,
                                  "Erro ao solicitar importação, tente novamente mais tarde.");
                            }

                            Navigator.of(context).pop();
                          }),
                    )
                : null,
          ),
        ),
        child: SingleChildScrollView(
          child: Column(
            children: [
              SizedBox(
                height: 32,
              ),
              CupertinoTextField(
                controller: _tickerController,
                autofocus: true,
                onChanged: (something) {
                  setState(() {});
                },
                decoration: BoxDecoration(),
                textInputAction: TextInputAction.next,
                inputFormatters: [UpperCaseTextFormatter()],
                keyboardType: TextInputType.text,
                prefix: Container(
                  width: 120,
                  padding: EdgeInsets.all(16),
                  child: Text(
                    'Ativo  ',
                    style: textTheme.textStyle
                        .copyWith(fontWeight: FontWeight.w400),
                  ),
                ),
                placeholder: "Código do ativo",
              ),
              CupertinoTextField(
                controller: _brokerController,
                onChanged: (something) {
                  setState(() {});
                },
                textInputAction: TextInputAction.next,
                keyboardType: TextInputType.text,
                prefix: Container(
                  width: 120,
                  padding: EdgeInsets.all(16),
                  child: Text(
                    'Corretora',
                    style: textTheme.textStyle
                        .copyWith(fontWeight: FontWeight.w400),
                  ),
                ),
                placeholder: "Corretora (opcional)",
              ),
              CupertinoTextField(
                controller: _amountController,
                onChanged: (something) {
                  setState(() {});
                },
                decoration: BoxDecoration(),
                textInputAction: TextInputAction.next,
                keyboardType: TextInputType.number,
                prefix: Container(
                  width: 120,
                  padding: EdgeInsets.all(16),
                  child: Text(
                    'Quantidade',
                    overflow: TextOverflow.ellipsis,
                    style: textTheme.textStyle
                        .copyWith(fontWeight: FontWeight.w400),
                  ),
                ),
                placeholder: "Quantidade",
              ),
              CupertinoTextField(
                controller: _priceController,
                onChanged: (something) {
                  setState(() {});
                },
                textInputAction: TextInputAction.next,
                inputFormatters: [moneyInputFormatter],
                keyboardType: TextInputType.number,
                prefix: Container(
                  width: 118,
                  padding: EdgeInsets.all(16),
                  child: Text(
                    'Preço ',
                    style: textTheme.textStyle
                        .copyWith(fontWeight: FontWeight.w400),
                  ),
                ),
                placeholder: "Preço",
              ),
              CupertinoTextField(
                controller: _dateController,
                onChanged: (something) {
                  setState(() {});
                },
                decoration: BoxDecoration(),
                inputFormatters: [dateInputFormatter],
                textInputAction: TextInputAction.next,
                keyboardType: TextInputType.number,
                prefix: Container(
                  width: 120,
                  padding: EdgeInsets.all(16),
                  child: Text(
                    'Data',
                    style: textTheme.textStyle
                        .copyWith(fontWeight: FontWeight.w400),
                  ),
                ),
                placeholder: "dd/mm/aaaa",
              ),
              CupertinoTextField(
                controller: _costsController,
                onChanged: (something) {
                  setState(() {});
                },
                textInputAction: TextInputAction.next,
                inputFormatters: [moneyInputFormatter],
                keyboardType: TextInputType.numberWithOptions(decimal: true),
                prefix: Container(
                  width: 120,
                  padding: EdgeInsets.all(16),
                  child: Text(
                    'Custos',
                    style: textTheme.textStyle
                        .copyWith(fontWeight: FontWeight.w400),
                  ),
                ),
                placeholder: "Custos (opcional)",
              ),
            ],
          ),
        ));
  }
}
