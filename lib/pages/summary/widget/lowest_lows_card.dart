import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/common/formatter/brazil.dart';
import 'package:goatfolio/common/widget/pressable_card.dart';
import 'package:goatfolio/pages/summary/screen/highest.dart';
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
    lows = (widget.performance.stocks + widget.performance.reits)
        .where((stock) => stock.currentDayChangePercent < 0)
        .toList()
          ..sort((a, b) =>
              a.currentDayChangePercent.compareTo(b.currentDayChangePercent));
  }

  Widget buildTopFive(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;

    if (lows.length == 0) {
      return Expanded(
        child: Center(
          child: Padding(
            padding: EdgeInsets.only(bottom: 16),
            child: Text("Nenhum", style: textTheme.textStyle),
          ),
        ),
      );
    }
    int listSize = lows.length > 3 ? 3 : lows.length;
    List<Widget> list = [];
    list.add(
      Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                "Ativo",
                style: textTheme.textStyle.copyWith(fontSize: 16),
              ),
              // Text(
              //   "Preço",
              //   style: Theme.of(context).textTheme.bodyText2,
              // ),
              Text(
                "Hoje",
                style: textTheme.textStyle.copyWith(fontSize: 16),
              ),
            ],
          ),
          SizedBox(
            height: 8,
          )
        ],
      ),
    );
    for (int i = 0; i < listSize; i++) {
      StockPerformance stock = lows[i];
      list.add(Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            stock.ticker,
            style: textTheme.textStyle.copyWith(fontSize: 14),
          ),
          Text(
            percentFormatter.format(stock.currentDayChangePercent / 100),
            style:
                textTheme.textStyle.copyWith(fontSize: 14, color: Colors.red),
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
      height: 226,
      child: PressableCard(
        cardPadding: EdgeInsets.only(left: 4, right: 16, top: 16, bottom: 16),
        onPressed: () => goToHighestPage(context, widget.performance, sortAscending: true),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            children: [
              Container(
                alignment: Alignment.centerLeft,
                child: Text(
                  "Maiores Baixas",
                  style: CupertinoTheme.of(context).textTheme.navTitleTextStyle,
                ),
              ),
              SizedBox(
                height: 16,
              ),
            ]..add(buildTopFive(context)),
          ),
        ),
      ),
    );
  }
}
