import 'package:flutter/cupertino.dart';
import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:goatfolio/services/investment/model/stock.dart';
import 'package:goatfolio/services/investment/service/stock_investment_service.dart';
import 'package:goatfolio/utils/dialog.dart' as dialog;
import 'package:goatfolio/utils/formatters.dart';
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

class NameChangeAdd extends StatefulWidget {
  final String title;
  final DateTime? date;
  final UserService userService;
  final String? ticker;
  final String? newTicker;

  const NameChangeAdd(
      {Key? key,
      required this.title,
      required this.userService,
      this.ticker,
      this.date,
      this.newTicker})
      : super(key: key);

  @override
  _NameChangeAddState createState() => _NameChangeAddState();
}

class _NameChangeAddState extends State<NameChangeAdd> {
  final TextEditingController _tickerController = TextEditingController();
  final TextEditingController _newTickerController = TextEditingController();
  final TextEditingController _dateController = TextEditingController();

  late StockInvestmentService service;
  late Future _future;

  @override
  void initState() {
    super.initState();
    service = StockInvestmentService(widget.userService);
    _tickerController.text = widget.ticker ?? '';
    _newTickerController.text = widget.newTicker ?? '';
    if (widget.date != null) {
      _dateController.text = DateFormat('dd/MM/yyyy').format(widget.date!);
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
            widget.title,
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
                controller: _newTickerController,
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
                    'Novo ativo ',
                    style: textTheme.textStyle
                        .copyWith(fontWeight: FontWeight.w400),
                  ),
                ),
                placeholder: "Código do novo ativo",
                enableSuggestions: false,
                autocorrect: false,
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
    if (_newTickerController.text.length < 5 ||
        _newTickerController.text.length > 6) {
      problems.add("Código do novo ativo inválido.");
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

    // final investment = StockInvestment(
    //     id: widget.id,
    //     ticker: _tickerController.text,
    //     amount: int.parse(_amountController.text),
    //     price: getDoubleFromMoneyFormat(_priceController.text),
    //     type: 'STOCK',
    //     operation: widget.buyOperation ? 'BUY' : 'SELL',
    //     date: DateFormat('dd/MM/yyyy').parse(_dateController.text, true),
    //     broker: _brokerController.text,
    //     costs: getDoubleFromMoneyFormat(
    //         _costsController.text.isNotEmpty ? _costsController.text : '0.0'));
    //
    // if (widget.id != null) {
    //   _future = service.editInvestment(investment);
    // } else {
    //   _future = service.addInvestment(investment);
    // }

    // modal.showUnDismissibleModalBottomSheet(
    //   context,
    //   ProgressIndicatorScaffold(
    //       message: widget.id != null
    //           ? 'Editando investimento...'
    //           : 'Adicionando investimento...',
    //       future: _future,
    //       onFinish: () async {
    //         try {
    //           await _future;
    //           if (widget.origInvestment != null) {
    //             widget.origInvestment!.copy(investment);
    //           }
    //           await dialog.showSuccessDialog(
    //               context, "Investimento adicionado com sucesso");
    //         } catch (e) {
    //           await dialog.showErrorDialog(
    //               context, "Erro ao adicionar investimento.");
    //         }
    //         Navigator.of(context).pop();
    //       }),
    // );
  }

  bool canSubmit() {
    return _tickerController.text.isNotEmpty &&
        _newTickerController.text.isNotEmpty &&
        _dateController.text.isNotEmpty;
  }

  Future<void> submitRequest(StockInvestment investment) async {
    // _future = service.addInvestment(investment);
    return _future;
  }
}
