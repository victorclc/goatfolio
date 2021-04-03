import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/common/formatter/brazil.dart';
import 'package:goatfolio/services/performance/model/portfolio_performance.dart';
import 'package:goatfolio/services/performance/notifier/portfolio_performance_notifier.dart';
import 'package:provider/provider.dart';

void goToHighestPage(
    BuildContext context, PortfolioPerformance performance) async {
  await Navigator.push(
    context,
    CupertinoPageRoute(
      builder: (context) => HighestPage(performance: performance),
    ),
  );
}

class HighestPage extends StatelessWidget {
  final PortfolioPerformance performance;

  const HighestPage({Key key, this.performance}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;
    return CupertinoPageScaffold(
        navigationBar: CupertinoNavigationBar(
          backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
          previousPageTitle: "",
          middle: Text("Altas e Baixas"),
        ),
        child: SingleChildScrollView(
            child: SafeArea(
          child: Container(
              padding: EdgeInsets.all(16),
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Ticker',
                        style: textTheme.textStyle,
                      ),
                      Text(
                        'Ult. Preço',
                        style: textTheme.textStyle,
                      ),
                      Text(
                        'Variação',
                        style: textTheme.textStyle,
                      ),
                    ],
                  ),
                  SizedBox(
                    height: 32,
                  ),
                ]..add(buildList(context)),
              )),
        )));
  }

  Widget buildList(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;
    List<Widget> children = [];
    final stocks = performance.stocks
      ..sort((b, a) =>
          a.currentDayChangePercent.compareTo(b.currentDayChangePercent));

    stocks.forEach(
      (s) {
        children.add(Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(s.ticker, style: textTheme.textStyle.copyWith(fontSize: 14)),
            Text(moneyFormatter.format(s.currentStockPrice)),
            Text(
              percentFormatter.format(s.currentDayChangePercent / 100),
              style: textTheme.textStyle
                  .copyWith(fontSize: 14, color: Colors.green),
            ),
          ],
        ));
        children.add(SizedBox(
          height: 32,
        ));
      },
    );

    return Column(
      children: children,
    );
  }
}
