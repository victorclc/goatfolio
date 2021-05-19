import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/common/util/dialog.dart';
import 'package:goatfolio/common/util/modal.dart';
import 'package:goatfolio/common/util/navigator.dart';
import 'package:goatfolio/pages/add/screen/stock_add.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/investment/model/stock.dart';
import 'package:goatfolio/services/investment/service/stock_investment_service.dart';
import 'package:goatfolio/services/performance/model/portfolio_list.dart';
import 'package:settings_ui/settings_ui.dart';

void goToInvestmentList(BuildContext context, bool buyOperation,
    UserService userService, Future<PortfolioList> portfolioListFuture) async {
  await NavigatorUtils.push(
    context,
    (context) => InvestmentsList(
      buyOperation: buyOperation,
      userService: userService,
      future: portfolioListFuture,
    ),
  );
}

class InvestmentsList extends StatefulWidget {
  final bool buyOperation;
  final UserService userService;
  final Future<PortfolioList> future;

  const InvestmentsList(
      {Key key, @required this.buyOperation, this.userService, this.future})
      : super(key: key);

  @override
  _InvestmentsListState createState() => _InvestmentsListState();
}

class _InvestmentsListState extends State<InvestmentsList> {
  StockInvestmentService service;

  Future<void> onStockSubmit(Map values) async {
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
    service = StockInvestmentService(widget.userService);
  }

  List<SettingsSection> buildAlphabetSections(PortfolioList portfolio) {
    final stocks = (portfolio.stocks + portfolio.reits + portfolio.bdrs)
        .map((s) => s.currentTickerName)
        .toList()
          ..sort();
    final Map<String, List<String>> tickersByAlphabet = Map();

    for (String ticker in stocks) {
      if (!tickersByAlphabet.containsKey(ticker[0])) {
        tickersByAlphabet.putIfAbsent(ticker[0], () => []);
      }
      tickersByAlphabet[ticker[0]].add(ticker);
    }

    final List<SettingsSection> sections = [];
    for (String letter in tickersByAlphabet.keys) {
      sections.add(
        SettingsSection(
          title: letter,
          tiles: tickersByAlphabet[letter]
              .map(
                (ticker) => SettingsTile(
                  title: ticker,
                  onPressed: (context) =>
                      ModalUtils.showDragableModalBottomSheet(
                          context,
                          StockAdd(
                            ticker: ticker,
                            buyOperation: widget.buyOperation,
                            userService: widget.userService,
                          )),
                ),
              )
              .toList(),
        ),
      );
    }
    return sections;
  }

  @override
  Widget build(BuildContext context) {
    return CupertinoPageScaffold(
        navigationBar: CupertinoNavigationBar(
          backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
          previousPageTitle: "",
          trailing: widget.buyOperation
              ? IconButton(
                  alignment: Alignment.centerRight,
                  padding: EdgeInsets.all(0),
                  icon: Icon(CupertinoIcons.add),
                  onPressed: () => ModalUtils.showDragableModalBottomSheet(
                        context,
                        StockAdd(
                          buyOperation: widget.buyOperation,
                          userService: widget.userService,
                        ),
                      ))
              : null,
          middle: Text(widget.buyOperation ? "Compra" : "Venda"),
        ),
        child: SafeArea(
          child: Container(
            child: Column(
              children: [
                FutureBuilder(
                    future: widget.future,
                    builder: (context, snapshot) {
                      switch (snapshot.connectionState) {
                        case ConnectionState.none:
                        case ConnectionState.active:
                          break;
                        case ConnectionState.waiting:
                          return CupertinoActivityIndicator();
                        case ConnectionState.done:
                          if (snapshot.hasData) {
                            return Expanded(
                                child: SettingsList(
                              sections: buildAlphabetSections(snapshot.data),
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
