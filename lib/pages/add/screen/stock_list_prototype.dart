import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/common/util/dialog.dart';
import 'package:goatfolio/common/util/modal.dart';
import 'package:goatfolio/common/widget/multi_prompt.dart';
import 'package:goatfolio/pages/add/prompt/add_stock_prompt.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/investment/model/stock.dart';
import 'package:goatfolio/services/investment/service/stock_investment_service.dart';
import 'package:goatfolio/services/investment/storage/stock_investment.dart';
import 'package:provider/provider.dart';
import 'package:settings_ui/settings_ui.dart';

void goToInvestmentListPrototype(
    BuildContext context, bool buyOperation) async {
  await Navigator.push(
    context,
    CupertinoPageRoute(
      builder: (context) => InvestmentsListPrototype(
        buyOperation: buyOperation,
      ),
    ),
  );
}

class InvestmentsListPrototype extends StatefulWidget {
  final bool buyOperation;

  const InvestmentsListPrototype({Key key, @required this.buyOperation})
      : super(key: key);

  @override
  _InvestmentsLisPrototypetState createState() =>
      _InvestmentsLisPrototypetState();
}

class _InvestmentsLisPrototypetState extends State<InvestmentsListPrototype> {
  StockInvestmentStorage storage;
  StockInvestmentService service;
  Future<List<String>> _future;

  Future<void> onStockSubmit(Map values) async {
    print(values);
    final investment = StockInvestment(
      ticker: values['ticker'],
      amount: int.parse(values['amount']),
      price: double.parse(values['price']),
      date: DateTime.now(),
      //values['date'],
      costs: double.parse(values['costs']),
      broker: values['broker'],
      type: "STOCK",
      operation: widget.buyOperation ? "BUY" : "SELL",
    );
    try {
      print("DENTRO DO TRY");
      await service.addInvestment(investment);
    } catch (Exception) {
      await DialogUtils.showErrorDialog(
          context, "Erro ao adicionar operação, tente novamente.");
      return;
    }
    await DialogUtils.showSuccessDialog(
        context, "Operação adicionada com sucesso!");
  }

  @override
  void initState() {
    super.initState();
    final userService = Provider.of<UserService>(context, listen: false);
    storage = StockInvestmentStorage();
    service = StockInvestmentService(userService);
    _future = storage.getDistinctTickers();
  }

  @override
  Widget build(BuildContext context) {
    return CupertinoPageScaffold(
        navigationBar: CupertinoNavigationBar(
          previousPageTitle: "",
          trailing: IconButton(
            alignment: Alignment.centerRight,
            padding: EdgeInsets.all(0),
              icon: Icon(Icons.add),
              onPressed: () => ModalUtils.showUnDismissibleModalBottomSheet(
                    context,
                    MultiPrompt(
                      onSubmit: onStockSubmit,
                      promptRequests: [
                        StockTickerPrompt(),
                        StockAmountPrompt(),
                        StockPricePrompt(),
                        StockDatePrompt(),
                        StockBrokerPrompt(),
                        StockCostsPrompt(),
                      ],
                    ),
                  )),
          middle: Text(widget.buyOperation ? "Compra" : "Venda"),
        ),
        child: SafeArea(
          child: Container(
            child: Column(
              children: [
                FutureBuilder(
                    future: _future,
                    builder: (context, snapshot) {
                      switch (snapshot.connectionState) {
                        case ConnectionState.none:
                        case ConnectionState.active:
                          break;
                        case ConnectionState.waiting:
                          return CupertinoActivityIndicator();
                        case ConnectionState.done:
                          if (snapshot.hasData) {
                            print(snapshot.data);
                            final List<String> tickers = snapshot.data..sort();
                            print("abcd"[0]);
                            final Map<String, List<String>> tickersByAlphabet =
                                Map();
                            for (String ticker in tickers) {
                              if (!tickersByAlphabet.containsKey(ticker[0])) {
                                tickersByAlphabet.putIfAbsent(
                                    ticker[0], () => List());
                              }
                              tickersByAlphabet[ticker[0]].add(ticker);
                            }
                            final List<SettingsSection> sections = List();
                            for (String letter in tickersByAlphabet.keys) {
                              sections.add(SettingsSection(
                                title: letter,
                                tiles: tickersByAlphabet[letter]
                                    .map((e) => SettingsTile(
                                          onPressed: (context) => ModalUtils
                                              .showUnDismissibleModalBottomSheet(
                                            context,
                                            MultiPrompt(
                                              onSubmit: (values) async {
                                                values['ticker'] = e;
                                                await onStockSubmit(values);
                                              },
                                              promptRequests: [
                                                StockAmountPrompt(),
                                                StockPricePrompt(),
                                                StockDatePrompt(),
                                                StockBrokerPrompt(),
                                                StockCostsPrompt(),
                                              ],
                                            ),
                                          ),
                                          title: e,
                                        ))
                                    .toList(),
                              ));
                            }
                            return Expanded(
                                child: SettingsList(
                              sections: sections,
                            ));
                          }
                      }
                      return Container();
                    }),
              ],
            ),
          ),
        ));
  }
}
