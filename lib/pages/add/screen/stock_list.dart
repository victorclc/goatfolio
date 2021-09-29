import 'dart:io';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:goatfolio/common/bloc/loading/loading_state.dart';
import 'package:goatfolio/common/util/dialog.dart';
import 'package:goatfolio/common/util/modal.dart';
import 'package:goatfolio/common/util/navigator.dart';
import 'package:goatfolio/common/widget/platform_aware_progress_indicator.dart';
import 'package:goatfolio/pages/add/screen/stock_add.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/investment/model/stock.dart';
import 'package:goatfolio/services/investment/service/stock_investment_service.dart';
import 'package:goatfolio/services/performance/cubit/performance_cubit.dart';
import 'package:goatfolio/services/performance/model/portfolio_performance.dart';
import 'package:settings_ui/settings_ui.dart';

void goToInvestmentList(
    BuildContext context, bool buyOperation, UserService userService) async {
  await NavigatorUtils.push(
    context,
    (_) =>
        InvestmentsList(buyOperation: buyOperation, userService: userService),
  );
}

class InvestmentsList extends StatelessWidget {
  final bool buyOperation;
  final UserService userService;
  final StockInvestmentService service;

  InvestmentsList({Key key, @required this.buyOperation, this.userService})
      : this.service = StockInvestmentService(userService),
        super(key: key);

  Future<void> onStockSubmit(BuildContext context, Map values) async {
    final investment = StockInvestment(
      ticker: values['ticker'],
      amount: int.parse(values['amount']),
      price: double.parse(values['price']),
      date: DateTime.now(),
      //values['date'],
      costs: double.parse(values['costs']),
      broker: values['broker'],
      type: "STOCK",
      operation: buyOperation ? "BUY" : "SELL",
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

  List<SettingsSection> buildAlphabetSections(PortfolioPerformance portfolio) {
    final stocks = portfolio.allStocks
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
                  iosLikeTile: true,
                  onPressed: (context) =>
                      ModalUtils.showDragableModalBottomSheet(
                          context,
                          StockAdd(
                            ticker: ticker,
                            buyOperation: buyOperation,
                            userService: userService,
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
    if (Platform.isIOS) {
      return buildIos(context);
    }
    return buildAndroid(context);
  }

  Widget buildAndroid(BuildContext context) {
    final textColor =
        CupertinoTheme.of(context).textTheme.navTitleTextStyle.color;
    return Scaffold(
      appBar: AppBar(
        leading: BackButton(
          color: textColor,
        ),
        actions: buyOperation
            ? [
                IconButton(
                    alignment: Alignment.centerRight,
                    icon: Icon(CupertinoIcons.add),
                    color: CupertinoColors.activeBlue,
                    onPressed: () => ModalUtils.showDragableModalBottomSheet(
                          context,
                          StockAdd(
                            buyOperation: buyOperation,
                            userService: userService,
                          ),
                        ))
              ]
            : null,
        title: Text(
          buyOperation ? "Compra" : "Venda",
          style: TextStyle(color: textColor),
        ),
        backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
      ),
      backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
      body: buildContent(context),
    );
  }

  Widget buildIos(BuildContext context) {
    return CupertinoPageScaffold(
      navigationBar: CupertinoNavigationBar(
        backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
        previousPageTitle: "",
        trailing: buyOperation
            ? IconButton(
                alignment: Alignment.centerRight,
                padding: EdgeInsets.all(0),
                icon: Icon(CupertinoIcons.add),
                onPressed: () => ModalUtils.showDragableModalBottomSheet(
                      context,
                      StockAdd(
                        buyOperation: buyOperation,
                        userService: userService,
                      ),
                    ))
            : null,
        middle: Text(buyOperation ? "Compra" : "Venda"),
      ),
      child: buildContent(context),
    );
  }

  Widget buildContent(BuildContext context) {
    return SafeArea(
      child: Container(
        child: Column(
          children: [
            BlocBuilder<PerformanceCubit, LoadingState>(
              builder: (context, state) {
                if (state == LoadingState.LOADING) {
                  return PlatformAwareProgressIndicator();
                } else if (state == LoadingState.LOADED) {
                  return Expanded(
                    child: SettingsList(
                      sections: buildAlphabetSections(
                          BlocProvider.of<PerformanceCubit>(context, listen: false)
                              .portfolioPerformance),
                    ),
                  );
                } else {
                  return Container();
                }
              },
            ),
          ],
        ),
      ),
    );
  }
}
