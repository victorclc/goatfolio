import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/common/formatter/brazil.dart';
import 'package:goatfolio/common/widget/cupertino_sliver_page.dart';
import 'package:goatfolio/common/widget/expansion_tile_custom.dart';
import 'package:goatfolio/pages/portfolio/widget/donut_chart.dart';
import 'package:goatfolio/services/performance/model/portfolio_performance.dart';
import 'package:goatfolio/services/performance/model/stock_position.dart';
import 'package:goatfolio/services/performance/model/stock_performance.dart';
import 'package:goatfolio/services/performance/notifier/portfolio_performance_notifier.dart';
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

  PortfolioPerformance performance;

  @override
  Widget build(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;

    return CupertinoSliverPage(
        largeTitle: PortfolioPage.title,
        onRefresh: () async =>
            Provider.of<PortfolioPerformanceNotifier>(context, listen: false)
                .updatePerformance(),
        children: [
          FutureBuilder(
            future:
                Provider.of<PortfolioPerformanceNotifier>(context, listen: true)
                    .future,
            builder: (context, snapshot) {
              switch (snapshot.connectionState) {
                case ConnectionState.none:
                case ConnectionState.active:
                  break;
                case ConnectionState.waiting:
                  return CupertinoActivityIndicator();
                case ConnectionState.done:
                  if (snapshot.hasData) {
                    performance = snapshot.data;
                    return Column(
                      children: [
                        Container(
                          alignment: Alignment.centerLeft,
                          padding:
                              EdgeInsets.only(left: 16, bottom: 16, top: 8),
                          child: Text(
                            "Alocação",
                            style: textTheme.navTitleTextStyle,
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
                        SizedBox(
                          height: 16,
                        ),
                        Padding(
                          padding: const EdgeInsets.all(16),
                          child: Divider(
                            height: 0,
                            color: Colors.grey,
                          ),
                        ),
                        InvestmentTypeExpansionTile(
                          title: 'Ações/ETFs',
                          grossAmount: performance.stockGrossAmount,
                          items: performance.stocks,
                          colors: colors,
                          totalAmount: performance.grossAmount,
                          ibovHistory: performance.ibovHistory,
                        ),
                        InvestmentTypeExpansionTile(
                          title: 'FIIs',
                          grossAmount: performance.reitGrossAmount,
                          items: performance.reits,
                          colors: colors,
                          totalAmount: performance.grossAmount,
                          ibovHistory: performance.ibovHistory,
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
                      style: textTheme.textStyle),
                  Text(" as informações.",
                      style: textTheme.textStyle),
                  SizedBox(
                    height: 8,
                  ),
                  Text("Toque para tentar novamente.",
                      style: textTheme.textStyle),
                  CupertinoButton(
                    padding: EdgeInsets.all(0),
                    child: Icon(
                      Icons.refresh_outlined,
                      size: 32,
                    ),
                    onPressed: () {
                      Provider.of<PortfolioPerformanceNotifier>(context,
                              listen: false)
                          .updatePerformance();
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
    List<TickerTotals> data = [];

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
  final List<StockPosition> ibovHistory;

  InvestmentTypeExpansionTile(
      {Key key,
      this.title,
      this.grossAmount,
      this.totalAmount,
      this.items,
      this.colors, this.ibovHistory})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;

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
              color: colors.containsKey(title)
                  ? colors[title].toColor()
                  : Rgb.random().toColor(),
            ),
            Text(
              ' ' + title,
              style: textTheme.navTitleTextStyle,
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
                    style: textTheme.textStyle.copyWith(fontSize: 16),
                  ),
                ],
              ),
              Text(
                moneyFormatter.format(grossAmount),
                style: textTheme.textStyle.copyWith(fontSize: 16),
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
                    style: textTheme.textStyle.copyWith(fontSize: 16),
                  ),
                ],
              ),
              // 100000 100
              // 34000   x
              Text(
                percentFormatter
                    .format(totalAmount == 0 ? 0.0 : grossAmount / totalAmount),
                style: textTheme.textStyle.copyWith(fontSize: 16),
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
                ibovHistory: ibovHistory,
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
  final List<StockPosition> ibovHistory;

  const StockInvestmentSummaryItem(
      {Key key,
      @required this.performance,
      this.portfolioTotalAmount,
      @required this.color,
      this.typeTotalAmount, this.ibovHistory})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;

    final currentValue = performance.currentAmount *
        (performance.currentStockPrice != null
            ? performance.currentStockPrice
            : 0.0);
    return CupertinoButton(
      padding: EdgeInsets.zero,
      onPressed: () {
        navigateToInvestmentDetails(context, performance, color, ibovHistory);
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
                    style: textTheme.textStyle.copyWith(
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
                      style: textTheme.textStyle.copyWith(fontSize: 16),
                    ),
                  ],
                ),
                Text(
                  moneyFormatter.format(currentValue),
                  style: textTheme.textStyle.copyWith(fontSize: 16),
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
                      style: textTheme.textStyle.copyWith(fontSize: 16),
                    ),
                  ],
                ),
                Text(
                  moneyFormatter
                      .format(currentValue - performance.currentInvested),
                  style: textTheme.textStyle.copyWith(
                      fontSize: 16,
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
                      style: textTheme.textStyle.copyWith(fontSize: 16),
                    ),
                  ],
                ),
                Text(
                  percentFormatter.format((performance.currentStockPrice *
                          performance.currentAmount) /
                      typeTotalAmount),
                  style: textTheme.textStyle.copyWith(fontSize: 16),
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
                      style: textTheme.textStyle.copyWith(fontSize: 16),
                    ),
                  ],
                ),
                Text(
                  percentFormatter.format((performance.currentStockPrice *
                          performance.currentAmount) /
                      portfolioTotalAmount),
                  style: textTheme.textStyle.copyWith(fontSize: 16),
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
