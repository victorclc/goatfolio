import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/common/formatter/brazil.dart';
import 'package:goatfolio/common/widget/pressable_card.dart';
import 'package:goatfolio/services/performance/model/portfolio_performance.dart';
import 'package:goatfolio/services/performance/model/stock_performance.dart';

class LowestLowsCard extends StatefulWidget {
  final PortfolioPerformance performance;

  const LowestLowsCard(this.performance, {Key key}) : super(key: key);

  @override
  _LowestLowsCardState createState() => _LowestLowsCardState();
}

class _LowestLowsCardState extends State<LowestLowsCard> {
  List<StockPerformance> lows;

  @override
  void initState() {
    super.initState();
    lows = widget.performance.stocks
        .where((stock) => stock.currentDayChangePercent < 0)
        .toList()
      ..sort((a, b) =>
          a.currentDayChangePercent.compareTo(b.currentDayChangePercent));
  }

  Widget buildTopFive() {
    if (lows.length == 0) {
      return Text("Nenhuma baixa", style: Theme.of(context).textTheme.subtitle1);
    }
    int listSize = lows.length > 5 ? 5 : lows.length;
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
              Text(
                "Preço",
                style: Theme.of(context).textTheme.bodyText2,
              ),
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
      StockPerformance stock = lows[i];
      list.add(Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(stock.ticker),
          Text(moneyFormatter.format(stock.currentStockPrice)),
          Text(
            percentFormatter.format(stock.currentDayChangePercent / 100),
            style: Theme.of(context)
                .textTheme
                .bodyText2
                .copyWith(color: Colors.red),
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
      child: PressableCard(
        onPressed: () => {},
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            children: [
              Container(
                alignment: Alignment.centerLeft,
                child: Text(
                  "Maiores Baixas",
                  style: Theme.of(context).textTheme.headline6,
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
