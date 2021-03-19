import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/common/formatter/brazil.dart';
import 'package:goatfolio/common/widget/pressable_card.dart';
import 'package:goatfolio/services/performance/model/portfolio_performance.dart';
import 'package:goatfolio/services/performance/model/stock_performance.dart';

class HighestHighsCard extends StatefulWidget {
  final PortfolioPerformance performance;

  const HighestHighsCard(this.performance, {Key key}) : super(key: key);

  @override
  _HighestHighsState createState() => _HighestHighsState();
}

class _HighestHighsState extends State<HighestHighsCard> {
  List<StockPerformance> highs;

  @override
  void initState() {
    super.initState();
    highs = widget.performance.stocks
        .where((stock) => stock.currentDayChangePercent >= 0)
        .toList()
          ..sort((b, a) =>
              a.currentDayChangePercent.compareTo(b.currentDayChangePercent));
  }

  Widget buildTopFive() {
    if (highs.length == 0) {
      return Text("Nenhum", style: Theme.of(context).textTheme.subtitle1);
    }
    int listSize = highs.length > 3 ? 3 : highs.length;
    List<Widget> list = List();
    list.add(
      Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                "Ticker",
                style: Theme.of(context).textTheme.bodyText2,
              ),
              // Text(
              //   "Preço",
              //   style: Theme.of(context).textTheme.bodyText2,
              // ),
              Text(
                "Hoje",
                style: Theme.of(context).textTheme.bodyText2,
              ),
            ],
          ),
          SizedBox(height: 8,)
        ],
      ),
    );
    for (int i = 0; i < listSize; i++) {
      StockPerformance stock = highs[i];
      list.add(Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(stock.ticker),
          // Text(moneyFormatter.format(stock.currentStockPrice)),
          Text(
            percentFormatter.format(stock.currentDayChangePercent / 100),
            style: Theme.of(context)
                .textTheme
                .bodyText2
                .copyWith(color: Colors.green),
          ),
        ],
      ));
      list.add(
        Divider(
          height: 16,
          color: Colors.grey,
        ),
      );
    }
    return Column(
      children: list,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      height: 224,
      child: PressableCard(
        cardPadding: EdgeInsets.only(left: 16, right: 4, top: 16, bottom: 16),
        onPressed: () => {},
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            children: [
              Container(
                alignment: Alignment.centerLeft,
                child: Text(
                  "Maiores Altas",
                  style: CupertinoTheme.of(context).textTheme.navTitleTextStyle,
                ),
              ),
              SizedBox(
                height: 16,
              ),
            ]..add(buildTopFive()),
          ),
        ),
      ),
    );
  }
}
