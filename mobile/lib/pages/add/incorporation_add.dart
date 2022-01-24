import 'package:flutter/cupertino.dart';
import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:goatfolio/services/corporate_events/client/client.dart';
import 'package:goatfolio/services/corporate_events/model/incorporation_event.dart';
import 'package:goatfolio/utils/dialog.dart' as dialog;
import 'package:goatfolio/utils/formatters.dart';
import 'package:goatfolio/widgets/progress_indicator_scaffold.dart';
import 'package:intl/intl.dart';
import 'package:goatfolio/utils/modal.dart' as modal;

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

class IncorporationAdd extends StatefulWidget {
  final String title;
  final DateTime? date;
  final int? initialAmount;
  final int? finalAmount;
  final UserService userService;
  final String? ticker;
  final String? newTicker;

  const IncorporationAdd(
      {Key? key,
      required this.title,
      required this.userService,
      this.ticker,
      this.date,
      this.initialAmount,
      this.finalAmount,
      this.newTicker})
      : super(key: key);

  @override
  _IncorporationAddState createState() => _IncorporationAddState();
}

class _IncorporationAddState extends State<IncorporationAdd> {
  final TextEditingController _tickerController = TextEditingController();
  final TextEditingController _newTickerController = TextEditingController();
  final TextEditingController _initialAmountController =
      TextEditingController();
  final TextEditingController _finalAmountController = TextEditingController();
  final TextEditingController _dateController = TextEditingController();

  late CorporateEventsClient service;
  late Future _future;

  @override
  void initState() {
    super.initState();
    service = CorporateEventsClient(widget.userService);
    _tickerController.text = widget.ticker ?? '';
    _newTickerController.text = widget.newTicker ?? '';
    if (widget.initialAmount != null) {
      _initialAmountController.text = '${widget.initialAmount}';
    }
    if (widget.finalAmount != null) {
      _finalAmountController.text = '${widget.finalAmount}';
    }
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
                autofocus: widget.newTicker == null ? true : false,
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
                controller: _initialAmountController,
                decoration: _kDefaultRoundedBorderDecoration,
                autofocus: widget.ticker != null && widget.initialAmount == null
                    ? true
                    : false,
                onChanged: (something) {
                  setState(() {});
                },
                textInputAction: TextInputAction.next,
                keyboardType: TextInputType.number,
                inputFormatters: [numberInputFormatter],
                prefix: Container(
                  width: 120,
                  padding: EdgeInsets.all(16),
                  child: Text(
                    'De',
                    style: textTheme.textStyle
                        .copyWith(fontWeight: FontWeight.w400),
                  ),
                ),
                placeholder: "Ex. 1",
                enableSuggestions: false,
                autocorrect: false,
              ),
              CupertinoTextField(
                controller: _finalAmountController,
                onChanged: (something) {
                  setState(() {});
                },
                decoration: _kDefaultRoundedBorderDecoration,
                textInputAction: TextInputAction.next,
                keyboardType: TextInputType.number,
                inputFormatters: [numberInputFormatter],
                prefix: Container(
                  width: 120,
                  padding: EdgeInsets.all(16),
                  child: Text(
                    'Para',
                    overflow: TextOverflow.ellipsis,
                    style: textTheme.textStyle
                        .copyWith(fontWeight: FontWeight.w400),
                  ),
                ),
                placeholder: "Ex. 2",
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
    if (int.parse(_finalAmountController.text) <= 0) {
      problems.add("Quantidade não pode ser 0.");
    }
    if (int.parse(_initialAmountController.text) <= 0) {
      problems.add("Quantidade não pode ser 0.");
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

    final event = IncorporationEvent(
      ticker: _tickerController.text,
      emittedTicker: _newTickerController.text,
      groupingFactor: int.parse(_initialAmountController.text) /
          int.parse(_finalAmountController.text),
      lastDatePrior: DateFormat('dd/MM/yyyy').parse(_dateController.text, true),
    );

    _future = service.addIncorporationEvent(event);

    modal.showUnDismissibleModalBottomSheet(
      context,
      ProgressIndicatorScaffold(
          message: "Adicionando evento corporativo",
          future: _future,
          onFinish: () async {
            try {
              final String message = await _future;
              await dialog.showSuccessDialog(context, message);
              Navigator.of(context).pop();
            } on Exception catch (e) {
              await dialog.showErrorDialog(
                  context, e.toString().replaceAll("Exception: ", ""));
            }
          }),
    );
  }

  bool canSubmit() {
    return _tickerController.text.isNotEmpty &&
        _newTickerController.text.isNotEmpty &&
        _initialAmountController.text.isNotEmpty &&
        _finalAmountController.text.isNotEmpty &&
        _dateController.text.isNotEmpty;
  }
}
