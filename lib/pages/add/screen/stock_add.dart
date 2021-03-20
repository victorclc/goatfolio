import 'package:flutter/cupertino.dart';
import 'package:goatfolio/common/formatter/brazil.dart';
import 'package:goatfolio/common/util/dialog.dart';
import 'package:goatfolio/common/util/modal.dart';
import 'package:goatfolio/common/widget/progress_indicator_scaffold.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/investment/model/stock.dart';
import 'package:goatfolio/services/investment/service/stock_investment_service.dart';
import 'package:intl/intl.dart';

class StockAdd extends StatefulWidget {
  final bool buyOperation;
  final UserService userService;
  final String ticker;

  const StockAdd(
      {Key key, this.buyOperation = true, this.userService, this.ticker})
      : super(key: key);

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
  StockInvestmentService service;
  Future _future;

  @override
  void initState() {
    super.initState();
    service = StockInvestmentService(widget.userService);
    _tickerController.text = widget.ticker ?? '';
  }

  bool canSubmit() {
    return _tickerController.text.isNotEmpty &&
        _brokerController.text.isNotEmpty &&
        _amountController.text.isNotEmpty &&
        _priceController.text.isNotEmpty &&
        _dateController.text.isNotEmpty;
  }

  Future<void> submitRequest(StockInvestment investment) async {
    _future = service.addInvestment(investment);
    return _future;
  }

  double getDoubleFromMoneyFormat(String formatted) {
    double value =
        double.parse(formatted.replaceAllMapped(RegExp(r'\D'), (match) {
      return '';
    }));
    return value / 100;
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
            widget.buyOperation ? 'Nova compra': 'Nova venda',
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
                ? () async {
                    try {
                      //TODO criar form valida campos e retornar uma mensagem esxplicando exatamente o q esta errado
                      final investment = StockInvestment(
                          ticker: _tickerController.text,
                          amount: int.parse(_amountController.text),
                          price:
                              getDoubleFromMoneyFormat(_priceController.text),
                          type: 'STOCK',
                          operation: widget.buyOperation ? 'BUY' : 'SELL',
                          date: DateFormat('dd/MM/yyyy')
                              .parse(_dateController.text),
                          broker: _brokerController.text,
                          costs: getDoubleFromMoneyFormat(
                              _costsController.text.isNotEmpty
                                  ? _costsController.text
                                  : '0.0'));

                      submitRequest(investment);
                    } catch (Exception) {
                      await DialogUtils.showErrorDialog(
                          context, "Dados invalidos.");
                      return;
                    }
                    ModalUtils.showUnDismissibleModalBottomSheet(
                      context,
                      ProgressIndicatorScaffold(
                          message: 'Adicionando investimento...',
                          future: _future,
                          onFinish: () async {
                            try {
                              await _future;
                              await DialogUtils.showSuccessDialog(context,
                                  "Investimento adicionado com sucesso");
                            } catch (Exceptions) {
                              await DialogUtils.showErrorDialog(
                                  context, "Erro ao adicionar investimento.");
                            }
                            Navigator.of(context).pop();
                          }),
                    );
                  }
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
                autofocus: widget.ticker == null ? true : false,
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
                autofocus: widget.ticker != null ? true : false,
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
