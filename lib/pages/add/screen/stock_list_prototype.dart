import 'package:alphabet_scroll_view/alphabet_scroll_view.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
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
                                tiles: tickersByAlphabet[letter].map(
                                  (e) => SettingsTile(
                                    title: e,
                                  ),
                                ).toList(),
                              ));
                            }
                            return Expanded(child: AlphabetScrollView(
                              list: sections.map((e) => AlphaModel(e.title)).toList(),
                              itemExtent: 230,
                              itemBuilder: (_, k, id) {
                                return Padding(
                                  padding: const EdgeInsets.only(right: 20),
                                  child: sections[k],
                                );
                              },
                            ),);
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
