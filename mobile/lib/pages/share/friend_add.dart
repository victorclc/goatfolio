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

class FriendAdd extends StatefulWidget {
  final UserService userService;

  const FriendAdd({Key? key, required this.userService}) : super(key: key);

  @override
  _FriendAddState createState() => _FriendAddState();
}

class _FriendAddState extends State<FriendAdd> {
  final TextEditingController _emailController = TextEditingController();
  late StockInvestmentService service;
  late Future _future;

  @override
  void initState() {
    super.initState();
    // service = StockInvestmentService(widget.userService);
    _emailController.text = '';
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
            "Compartilhar",
            style: textTheme.navTitleTextStyle,
          ),
          trailing: CupertinoButton(
            padding: EdgeInsets.all(0),
            child: Align(
              alignment: AlignmentDirectional.centerStart,
              widthFactor: 1.0,
              child: Text(
                'Enviar',
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
                controller: _emailController,
                autofocus: true,
                onChanged: (something) {
                  setState(() {});
                },
                decoration: _kDefaultRoundedBorderDecoration,
                textInputAction: TextInputAction.next,
                inputFormatters: [UpperCaseTextFormatter()],
                keyboardType: TextInputType.text,
                prefix: Container(
                  width: 80,
                  padding: EdgeInsets.all(16),
                  child: Text(
                    'Para',
                    style: textTheme.textStyle
                        .copyWith(fontWeight: FontWeight.w400),
                  ),
                ),
                placeholder: "e-mail",
                enableSuggestions: false,
                autocorrect: false,
              ),
            ],
          ),
        ));
  }

  List<String> validateForm() {
    return [""];
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
    //
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
    return _emailController.text.isNotEmpty;
  }

// Future<void> submitRequest() async {
//   _future = service.addInvestment(investment);
//   return _future;
// }

}
