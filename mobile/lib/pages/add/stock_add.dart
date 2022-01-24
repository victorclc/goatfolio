import 'package:flutter/cupertino.dart';
import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:goatfolio/services/investment/model/stock.dart';
import 'package:goatfolio/services/investment/service/stock_investment_service.dart';
import 'package:goatfolio/utils/dialog.dart' as dialog;
import 'package:goatfolio/utils/formatters.dart';
import 'package:goatfolio/utils/modal.dart' as modal;
import 'package:goatfolio/widgets/progress_indicator_scaffold.dart';

import 'package:intl/intl.dart';

const BorderSide _kDefaultRoundedBorderSide = BorderSide(
  color: CupertinoDynamicColor.withBrightness(
    color: Color(0x33000000),
    darkColor: Color(0x33FFFFFF),
  ),
  style: BorderStyle.solid,
  width: 0.0,
);

const Border _kDefaultRoundedBorder = Border(
  bottom: _kDefaultRoundedBorderSide,
);

const BoxDecoration _kDefaultRoundedBorderDecoration = BoxDecoration(
  color: CupertinoDynamicColor.withBrightness(
    color: CupertinoColors.white,
    darkColor: CupertinoColors.black,
  ),
  border: _kDefaultRoundedBorder,
  // borderRadius: BorderRadius.all(Radius.circular(5.0)),
);

class StockAdd extends StatefulWidget {
  final bool buyOperation;
  final UserService userService;
  final String? ticker;
  final String? broker;
  final int? amount;
  final double? price;
  final DateTime? date;
  final double? costs;
  final String? id;
  final StockInvestment? origInvestment;

  const StockAdd(
      {Key? key,
      this.buyOperation = true,
      required this.userService,
      this.ticker,
      this.broker,
      this.amount,
      this.price,
      this.date,
      this.costs,
      this.id,
      this.origInvestment})
      : super(key: key);

  StockAdd.fromStockInvestment(this.origInvestment,
      {required UserService userService})
      : buyOperation = origInvestment!.operation == 'BUY',
        ticker = origInvestment.ticker,
        broker = origInvestment.broker,
        amount = origInvestment.amount,
        price = origInvestment.price,
        date = origInvestment.date,
        costs = origInvestment.costs,
        id = origInvestment.id,
        userService = userService;

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
  late StockInvestmentService service;
  late Future _future;

  @override
  void initState() {
    super.initState();
    service = StockInvestmentService(widget.userService);
    _tickerController.text = widget.ticker ?? '';
    _brokerController.text = widget.broker ?? '';
    if (widget.amount != null) {
      _amountController.text = '${widget.amount}';
    }
    if (widget.price != null) {
      _priceController.text =
          moneyInputFormatter.format(widget.price!.toStringAsFixed(2));
    }
    if (widget.date != null) {
      _dateController.text = DateFormat('dd/MM/yyyy').format(widget.date!);
    }
    if (widget.costs != null) {
      _costsController.text = moneyInputFormatter.format("${widget.costs}");
    }
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
            widget.buyOperation ? 'Nova compra' : 'Nova venda',
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
            onPressed: canSubmit() ? onSubmit : null,
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
                decoration: _kDefaultRoundedBorderDecoration,
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
                enableSuggestions: false,
                autocorrect: false,
              ),
              CupertinoTextField(
                controller: _brokerController,
                decoration: _kDefaultRoundedBorderDecoration,
                autofocus: widget.ticker != null && widget.broker == null
                    ? true
                    : false,
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
                placeholder: "Corretora",
                enableSuggestions: false,
                autocorrect: false,
              ),
              CupertinoTextField(
                controller: _amountController,
                onChanged: (something) {
                  setState(() {});
                },
                decoration: _kDefaultRoundedBorderDecoration,
                inputFormatters: [numberInputFormatter],
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
                decoration: _kDefaultRoundedBorderDecoration,
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
                decoration: _kDefaultRoundedBorderDecoration,
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
              // CupertinoTextField(
              //   controller: _costsController,
              //   decoration: _kDefaultRoundedBorderDecoration,
              //   onChanged: (something) {
              //     setState(() {});
              //   },
              //   textInputAction: TextInputAction.next,
              //   inputFormatters: [moneyInputFormatter],
              //   keyboardType: TextInputType.numberWithOptions(decimal: true),
              //   prefix: Container(
              //     width: 120,
              //     padding: EdgeInsets.all(16),
              //     child: Text(
              //       'Custos',
              //       style: textTheme.textStyle
              //           .copyWith(fontWeight: FontWeight.w400),
              //     ),
              //   ),
              //   placeholder: "Custos (opcional)",
              // ),
            ],
          ),
        ));
  }

  List<String> validateForm() {
    final List<String> problems = [];
    if (_tickerController.text.length < 5 ||
        _tickerController.text.length > 6) {
      problems.add("Código do ativo inválido.");
    }
    if (int.parse(_amountController.text) <= 0) {
      problems.add("Quantidade não pode ser 0.");
    }
    if (getDoubleFromMoneyFormat(_priceController.text) <= 0) {
      problems.add("O preço não pode ser R\$ 0,00.");
    }
    if (getDoubleFromMoneyFormat(
            _costsController.text.isNotEmpty ? _costsController.text : '0.0') <
        0) {
      problems.add("O custo não pode ser negativo.");
    }
    if (_dateController.text.length != 10) {
      problems.add("Data inválida.");
    } else {
      final splittedDate = _dateController.text.split("/");
      final day = int.parse(splittedDate[0]);
      final month = int.parse(splittedDate[1]);
      if (day > 31 || month > 12) {
        problems.add("Data inválida.");
      }
      if (DateFormat('dd/MM/yyyy')
              .parse(_dateController.text)
              .compareTo(DateTime.now()) >
          0) {
        problems.add("Data inválida.");
      }
    }
    return problems;
  }

  void onSubmit() async {
    try {
      final problems = validateForm();
      if (problems.isNotEmpty) {
        final List<Widget> problemWidgets = [];
        problems.forEach((description) {
          problemWidgets.add(Text(description));
        });
        await dialog.showCustomErrorDialog(
            context,
            Column(
              children: problemWidgets,
            ));
        return;
      }
    } on Exception catch (e) {
      await dialog.showErrorDialog(context, "Dados invalidos.");
      return;
    }

    final investment = StockInvestment(
        id: widget.id,
        ticker: _tickerController.text,
        amount: int.parse(_amountController.text),
        price: getDoubleFromMoneyFormat(_priceController.text),
        type: 'STOCK',
        operation: widget.buyOperation ? 'BUY' : 'SELL',
        date: DateFormat('dd/MM/yyyy').parse(_dateController.text, true),
        broker: _brokerController.text,
        costs: getDoubleFromMoneyFormat(
            _costsController.text.isNotEmpty ? _costsController.text : '0.0'));

    if (widget.id != null) {
      _future = service.editInvestment(investment);
    } else {
      _future = service.addInvestment(investment);
    }

    modal.showUnDismissibleModalBottomSheet(
      context,
      ProgressIndicatorScaffold(
          message: widget.id != null
              ? 'Editando investimento...'
              : 'Adicionando investimento...',
          future: _future,
          onFinish: () async {
            try {
              await _future;
              if (widget.origInvestment != null) {
                widget.origInvestment!.copy(investment);
              }
              await dialog.showSuccessDialog(
                  context, "Investimento adicionado com sucesso");
            } catch (e) {
              await dialog.showErrorDialog(
                  context, "Erro ao adicionar investimento.");
            }
            Navigator.of(context).pop();
          }),
    );
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
}
