import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/common/formatter/brazil.dart';
import 'package:goatfolio/common/widget/cupertino_sliver_page.dart';
import 'package:goatfolio/common/widget/expansion_tile_custom.dart';
import 'package:goatfolio/pages/portfolio/widget/donut_chart.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/performance/client/performance_client.dart';
import 'package:goatfolio/services/performance/model/portfolio_performance.dart';
import 'package:goatfolio/services/performance/model/stock_performance.dart';
import 'package:provider/provider.dart';

import 'dart:math' as math;
import 'package:charts_flutter/flutter.dart' as charts;

import 'investment_details.dart';

class PortfolioPage extends StatefulWidget {
  static const title = 'Portfolio';
  static const icon = Icon(Icons.trending_up);

  @override
  _PortfolioPageState createState() => _PortfolioPageState();
}

class _PortfolioPageState extends State<PortfolioPage> {
  Map<String, Rgb> colors = Map();
  Future<PortfolioPerformance> _future;
  PerformanceClient client;
  PortfolioPerformance performance;

  @override
  void initState() {
    super.initState();
    final userService = Provider.of<UserService>(context, listen: false);
    client = PerformanceClient(userService);
    _future = getPortfolioPerformance();
  }

  Future<PortfolioPerformance> getPortfolioPerformance() async {
    performance = await client.getPortfolioPerformance();
    return performance;
  }

  @override
  Widget build(BuildContext context) {
    return CupertinoSliverPage(
        largeTitle: PortfolioPage.title,
        onRefresh: () async {
          _future = getPortfolioPerformance();
          await _future;
          setState(() {});
        },
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
                    return Column(
                      children: [
                        Container(
                          alignment: Alignment.centerLeft,
                          padding:
                              EdgeInsets.only(left: 16, bottom: 16, top: 8),
                          child: Text(
                            "Alocação",
                            style:
                                Theme.of(context).textTheme.bodyText2.copyWith(
                                      fontSize: 16,
                                      fontWeight: FontWeight.bold,
                                    ),
                          ),
                        ),
                        SizedBox(
                          height: 240,
                          width: double.infinity,
                          child: DonutAutoLabelChart(
                            typeSeries: buildSubtypeSeries(),
                            stocksSeries: buildStockSeries(),
                            reitsSeries: buildReitSeries(),
                          ),
                        ),
                        InvestmentTypeExpansionTile(
                          title: 'Ações/ETFs',
                          grossAmount: performance.stockGrossAmount,
                          items: performance.stocks,
                          colors: colors,
                          totalAmount: performance.grossAmount,
                        ),
                        InvestmentTypeExpansionTile(
                          title: 'FIIs',
                          grossAmount: performance.reitGrossAmount,
                          items: performance.reits,
                          colors: colors,
                          totalAmount: performance.grossAmount,
                        ),
                      ],
                    );
                  }
              }
              return Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  SizedBox(
                    height: 32,
                  ),
                  Text("Tivemos um problema ao carregar",
                      style: Theme.of(context).textTheme.subtitle1),
                  Text(" as informações.",
                      style: Theme.of(context).textTheme.subtitle1),
                  SizedBox(
                    height: 8,
                  ),
                  Text("Toque para tentar novamente.",
                      style: Theme.of(context).textTheme.subtitle1),
                  CupertinoButton(
                    padding: EdgeInsets.all(0),
                    child: Icon(
                      Icons.refresh_outlined,
                      size: 32,
                    ),
                    onPressed: () {
                      setState(() {
                        _future = getPortfolioPerformance();
                      });
                    },
                  ),
                ],
              );
            },
          ),
        ]);
  }

  List<charts.Series<TickerTotals, String>> buildStockSeries() {
    final stocks = performance.stocks;
    List<TickerTotals> data = stocks.map((p) {
      final color = Rgb.random();
      colors[p.ticker] = color;
      if (p.currentAmount <= 0) {
        return null;
      }
      return TickerTotals(
          p.ticker, p.currentAmount * p.currentStockPrice, color);
    }).toList()
      ..removeWhere((element) => element == null);
    print("Builded series");
    print(data);
    return [
      new charts.Series<TickerTotals, String>(
        id: 'stocks',
        domainFn: (TickerTotals totals, _) => totals.ticker,
        measureFn: (TickerTotals totals, _) => totals.total,
        data: data,
        colorFn: (totals, _) => charts.Color(
            r: totals.color.r, g: totals.color.g, b: totals.color.b),
        // Set a label accessor to control the text of the arc label.
        labelAccessorFn: (TickerTotals totals, _) =>
            '${totals.ticker.replaceAll('.SA', '')}',
      )
    ];
  }

  List<charts.Series<TickerTotals, String>> buildReitSeries() {
    final stocks = performance.reits;
    List<TickerTotals> data = stocks.map((p) {
      final color = Rgb.random();
      colors[p.ticker] = color;
      if (p.currentAmount <= 0) {
        return null;
      }
      return TickerTotals(
          p.ticker, p.currentAmount * p.currentStockPrice, color);
    }).toList()
      ..removeWhere((element) => element == null);
    print("Builded series");
    print(data);
    return [
      new charts.Series<TickerTotals, String>(
        id: 'reits',
        domainFn: (TickerTotals totals, _) => totals.ticker,
        measureFn: (TickerTotals totals, _) => totals.total,
        data: data,
        colorFn: (totals, _) => charts.Color(
            r: totals.color.r, g: totals.color.g, b: totals.color.b),
        // Set a label accessor to control the text of the arc label.
        labelAccessorFn: (TickerTotals totals, _) =>
            '${totals.ticker.replaceAll('.SA', '')}',
      )
    ];
  }

  List<charts.Series<TickerTotals, String>> buildSubtypeSeries() {
    List<TickerTotals> data = List();

    if (performance.stockGrossAmount > 0) {
      colors['Ações/ETFs'] = Rgb.random();
      data.add(TickerTotals(
          'Ações/ETFs', performance.stockGrossAmount, colors['Ações/ETFs']));
    }
    if (performance.reitGrossAmount > 0) {
      colors['FIIs'] = Rgb.random();
      data.add(
          TickerTotals('FIIs', performance.reitGrossAmount, colors['FIIs']));
    }

    return [
      new charts.Series<TickerTotals, String>(
        id: 'Subtypes',
        domainFn: (TickerTotals totals, _) => totals.ticker,
        measureFn: (TickerTotals totals, _) => totals.total,
        data: data,
        colorFn: (totals, _) => charts.Color(
            r: colors[totals.ticker].r,
            g: colors[totals.ticker].g,
            b: colors[totals.ticker].b),
        // Set a label accessor to control the text of the arc label.
        labelAccessorFn: (TickerTotals totals, _) =>
            '${totals.ticker.replaceAll('.SA', '')}',
      )
    ];
  }
}

class TickerTotals {
  String ticker;
  double total;
  Rgb color;

  TickerTotals(this.ticker, this.total, this.color);
}

class Rgb {
  final int r;
  final int g;
  final int b;

  Rgb(this.r, this.g, this.b);

  Color toColor() {
    return Color.fromARGB(0xFF, this.r, this.g, this.b);
  }

  static Rgb random() {
    return Rgb(
        (math.Random().nextDouble() * 0xFF).toInt(),
        (math.Random().nextDouble() * 0xFF).toInt(),
        (math.Random().nextDouble() * 0xFF).toInt());
  }
}

class InvestmentTypeExpansionTile extends StatelessWidget {
  final String title;
  final double grossAmount;
  final double totalAmount;
  final List<StockPerformance> items;
  final Map<String, Rgb> colors;

  InvestmentTypeExpansionTile(
      {Key key,
      this.title,
      this.grossAmount,
      this.totalAmount,
      this.items,
      this.colors})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(left: 8, right: 8),
      child: ExpansionTileCustom(
        initiallyExpanded: true,
        childrenPadding: EdgeInsets.only(left: 8, right: 8),
        tilePadding: EdgeInsets.zero,
        title: Row(
          children: [
            Container(
              width: 4,
              height: 14,
              color: colors[title].toColor(),
            ),
            Text(
              ' ' + title,
              style: Theme.of(context).textTheme.bodyText2.copyWith(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
            ),
          ],
        ),
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: <Widget>[
              Row(
                children: <Widget>[
                  Text(
                    "Total em carteira",
                    style: Theme.of(context).textTheme.bodyText2,
                  ),
                ],
              ),
              Text(
                moneyFormatter.format(grossAmount),
                style: Theme.of(context).textTheme.bodyText2,
              ),
            ],
          ),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: <Widget>[
              Row(
                children: <Widget>[
                  Text(
                    "% do portfolio",
                    style: Theme.of(context).textTheme.bodyText2,
                  ),
                ],
              ),
              // 100000 100
              // 34000   x
              Text(
                percentFormatter.format(grossAmount / totalAmount),
                style: Theme.of(context).textTheme.bodyText2,
              ),
            ],
          ),
          SizedBox(
            height: 24,
          ),
          ListView.builder(
            padding: EdgeInsets.zero,
            physics: NeverScrollableScrollPhysics(),
            shrinkWrap: true,
            itemBuilder: (context, index) {
              final item = items[index];
              final Rgb rgb = colors[item.ticker];
              var color = rgb.toColor();

              return StockInvestmentSummaryItem(
                performance: item,
                color: color,
                portfolioTotalAmount: totalAmount,
                typeTotalAmount: grossAmount,
              );
            },
            itemCount: items.length,
          ),
        ],
      ),
    );
  }
}

class StockInvestmentSummaryItem extends StatelessWidget {
  final StockPerformance performance;
  final Color color;
  final double portfolioTotalAmount;
  final double typeTotalAmount;

  const StockInvestmentSummaryItem(
      {Key key,
      @required this.performance,
      this.portfolioTotalAmount,
      @required this.color, this.typeTotalAmount})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    final currentValue = performance.currentAmount *
        (performance.currentStockPrice != null
            ? performance.currentStockPrice
            : 0.0);
    return CupertinoButton(
      padding: EdgeInsets.zero,
      onPressed: () {
        navigateToInvestmentDetails(context, performance, color);
      },
      child: Container(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            Container(
              padding: EdgeInsets.only(bottom: 8),
              child: Row(
                children: <Widget>[
                  Container(
                    width: 4,
                    height: 14,
                    color: color,
                  ),
                  Text(
                    " ${performance.ticker.replaceAll('.SA', '')}",
                    style: Theme.of(context).textTheme.bodyText2.copyWith(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                  ),
                ],
              ),
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: <Widget>[
                Row(
                  children: <Widget>[
                    Text(
                      "Saldo atual",
                      style: Theme.of(context).textTheme.bodyText2,
                    ),
                  ],
                ),
                Text(
                  moneyFormatter.format(currentValue),
                  style: Theme.of(context).textTheme.bodyText2,
                ),
              ],
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: <Widget>[
                Row(
                  children: <Widget>[
                    Text(
                      "Resultado",
                      style: Theme.of(context).textTheme.bodyText2,
                    ),
                  ],
                ),
                Text(
                  moneyFormatter
                      .format(currentValue - performance.currentInvested),
                  style: Theme.of(context).textTheme.bodyText2.copyWith(
                      color: currentValue - performance.currentInvested < 0
                          ? Colors.red
                          : Colors.green),
                  // style: coloredStyle,
                ),
              ],
            ),
            SizedBox(
              height: 4,
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: <Widget>[
                Row(
                  children: <Widget>[
                    Text(
                      "% na categoria",
                      style: Theme.of(context).textTheme.bodyText2,
                    ),
                  ],
                ),
                Text(
                  percentFormatter.format((performance.currentStockPrice *
                      performance.currentAmount) /
                      typeTotalAmount),
                  style: Theme.of(context).textTheme.bodyText2,
                ),
              ],
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: <Widget>[
                Row(
                  children: <Widget>[
                    Text(
                      "% do portfolio",
                      style: Theme.of(context).textTheme.bodyText2,
                    ),
                  ],
                ),
                Text(
                  percentFormatter.format((performance.currentStockPrice *
                          performance.currentAmount) /
                      portfolioTotalAmount),
                  style: Theme.of(context).textTheme.bodyText2,
                ),
              ],
            ),
            Divider(
              height: 16,
              color: Colors.grey,
            ),
          ],
        ),
      ),
    );
  }
}
