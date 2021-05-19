import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/common/formatter/brazil.dart';
import 'package:goatfolio/common/widget/cupertino_sliver_page.dart';
import 'package:goatfolio/common/widget/expansion_tile_custom.dart';
import 'package:goatfolio/pages/portfolio/widget/donut_chart.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/performance/model/benchmark_position.dart';
import 'package:goatfolio/services/performance/model/portfolio_list.dart';
import 'package:goatfolio/services/performance/model/stock_summary.dart';
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

  PortfolioList portfolioList;

  @override
  Widget build(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;

    return CupertinoSliverPage(largeTitle: PortfolioPage.title, children: [
      FutureBuilder(
        future: Provider.of<PortfolioListNotifier>(context, listen: true)
            .futureList,
        builder: (context, snapshot) {
          switch (snapshot.connectionState) {
            case ConnectionState.none:
            case ConnectionState.active:
              break;
            case ConnectionState.waiting:
              return CupertinoActivityIndicator();
            case ConnectionState.done:
              if (snapshot.hasData) {
                portfolioList = snapshot.data;
                return Column(
                  children: [
                    Container(
                      alignment: Alignment.centerLeft,
                      padding: EdgeInsets.only(left: 16, bottom: 16, top: 8),
                      child: Text(
                        "Alocação",
                        style: textTheme.navTitleTextStyle,
                      ),
                    ),
                    SizedBox(
                      height: 240,
                      width: double.infinity,
                      child: DonutAutoLabelChart(
                          portfolioList: portfolioList,
                          typeSeries: buildSubtypeSeries(),
                          stocksSeries: buildStockSeries(),
                          reitsSeries: buildReitSeries(),
                          bdrsSeries: buildBdrSeries()),
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
                      grossAmount: portfolioList.stockGrossAmount,
                      items: portfolioList.stocks,
                      colors: colors,
                      totalAmount: portfolioList.grossAmount,
                      ibovHistory: portfolioList.ibovHistory,
                    ),
                    InvestmentTypeExpansionTile(
                      title: 'BDRs',
                      grossAmount: portfolioList.bdrGrossAmount,
                      items: portfolioList.bdrs,
                      colors: colors,
                      totalAmount: portfolioList.grossAmount,
                      ibovHistory: portfolioList.ibovHistory,
                    ),
                    InvestmentTypeExpansionTile(
                      title: 'FIIs',
                      grossAmount: portfolioList.reitGrossAmount,
                      items: portfolioList.reits,
                      colors: colors,
                      totalAmount: portfolioList.grossAmount,
                      ibovHistory: portfolioList.ibovHistory,
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
              Text(" as informações.", style: textTheme.textStyle),
              SizedBox(
                height: 8,
              ),
              Text("Toque para tentar novamente.", style: textTheme.textStyle),
              CupertinoButton(
                padding: EdgeInsets.all(0),
                child: Icon(
                  Icons.refresh_outlined,
                  size: 32,
                ),
                onPressed: () {
                  Provider.of<PortfolioListNotifier>(context, listen: false)
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
    final stocks = portfolioList.stocks;
    List<TickerTotals> data = stocks.map((p) {
      final color = Rgb.random();
      colors[p.ticker] = color;
      if (p.amount <= 0) {
        return null;
      }
      return TickerTotals(p.currentTickerName, p.grossAmount, color);
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
    final stocks = portfolioList.reits;
    List<TickerTotals> data = stocks.map((p) {
      final color = Rgb.random();
      colors[p.ticker] = color;
      if (p.amount <= 0) {
        return null;
      }
      return TickerTotals(p.ticker, p.grossAmount, color);
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

  List<charts.Series<TickerTotals, String>> buildBdrSeries() {
    final stocks = portfolioList.bdrs;
    List<TickerTotals> data = stocks.map((p) {
      final color = Rgb.random();
      colors[p.ticker] = color;
      if (p.amount <= 0) {
        return null;
      }
      return TickerTotals(p.currentTickerName, p.grossAmount, color);
    }).toList()
      ..removeWhere((element) => element == null);
    return [
      new charts.Series<TickerTotals, String>(
        id: 'bdrs',
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

    // #5c36ad
    // #ec1a72
    // #ff8c12
    final stockColor = Color(0x5c36ad);
    if (portfolioList.stockGrossAmount > 0) {
      colors['Ações/ETFs'] =
          Rgb(stockColor.red, stockColor.green, stockColor.blue);
      data.add(TickerTotals('Ações\ne ETFs', portfolioList.stockGrossAmount,
          colors['Ações/ETFs']));
    }
    final reitColor = Color(0xf52d6f);
    if (portfolioList.reitGrossAmount > 0) {
      colors['FIIs'] = Rgb(reitColor.red, reitColor.green, reitColor.blue);
      data.add(
          TickerTotals('FIIs', portfolioList.reitGrossAmount, colors['FIIs']));
    }

    final bdrColor = Color(0xffa514);
    if (portfolioList.bdrGrossAmount > 0) {
      colors['BDRs'] = Rgb(bdrColor.red, bdrColor.green, bdrColor.blue);
      data.add(
          TickerTotals('BDRs', portfolioList.reitGrossAmount, colors['BDRs']));
    }

    return [
      new charts.Series<TickerTotals, String>(
        id: 'Subtypes',
        domainFn: (TickerTotals totals, _) => totals.ticker,
        measureFn: (TickerTotals totals, _) => totals.total,
        data: data,
        colorFn: (totals, _) =>
            charts.ColorUtil.fromDartColor(totals.color.toColor()),
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
  final List<StockSummary> items;
  final Map<String, Rgb> colors;
  final List<BenchmarkPosition> ibovHistory;
  final bool initiallyExpanded;

  InvestmentTypeExpansionTile(
      {Key key,
      this.title,
      this.grossAmount,
      this.totalAmount,
      this.items,
      this.colors,
      this.ibovHistory,
      this.initiallyExpanded = false})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;

    final sortedItems = items
      ..sort((a, b) => a.currentTickerName.compareTo(b.currentTickerName));

    return Padding(
      padding: const EdgeInsets.only(left: 8, right: 8),
      child: ExpansionTileCustom(
        initiallyExpanded: initiallyExpanded,
        childrenPadding: EdgeInsets.only(left: 8, right: 8),
        tilePadding: EdgeInsets.zero,
        title: Column(
          children: [
            Row(
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
          ],
        ),
        subtitle: Padding(
          padding: const EdgeInsets.only(top: 8, bottom: 8),
          child: Column(
            children: [
              Padding(
                padding: const EdgeInsets.only(left: 8, right: 8),
                child: Row(
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
              ),
              Padding(
                padding: const EdgeInsets.only(left: 8, right: 8),
                child: Row(
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
                      percentFormatter.format(
                          totalAmount == 0 ? 0.0 : grossAmount / totalAmount),
                      style: textTheme.textStyle.copyWith(fontSize: 16),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        children: [
          SizedBox(
            height: 8,
          ),
          ListView.builder(
            padding: EdgeInsets.zero,
            physics: NeverScrollableScrollPhysics(),
            shrinkWrap: true,
            itemBuilder: (context, index) {
              final item = sortedItems[index];
              final Rgb rgb = colors[item.ticker];
              final color = rgb.toColor();

              return StockInvestmentSummaryItem(
                summary: item,
                color: color,
                portfolioTotalAmount: totalAmount,
                typeTotalAmount: grossAmount,
                ibovHistory: ibovHistory,
              );
            },
            itemCount: sortedItems.length,
          ),
        ],
      ),
    );
  }
}

class StockInvestmentSummaryItem extends StatelessWidget {
  final StockSummary summary;
  final Color color;
  final double portfolioTotalAmount;
  final double typeTotalAmount;
  final List<BenchmarkPosition> ibovHistory;

  const StockInvestmentSummaryItem(
      {Key key,
      @required this.summary,
      this.portfolioTotalAmount,
      @required this.color,
      this.typeTotalAmount,
      this.ibovHistory})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;
    final userService = Provider.of<UserService>(context, listen: false);
    final currentValue = summary.amount *
        (summary.currentPrice != null ? summary.currentPrice : 0.0);
    return CupertinoButton(
      padding: EdgeInsets.zero,
      onPressed: () {
        navigateToInvestmentDetails(
            context, summary, color, ibovHistory, userService);
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
                    " ${summary.currentTickerName.replaceAll('.SA', '')}",
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
                  moneyFormatter.format(currentValue - summary.investedAmount),
                  style: textTheme.textStyle.copyWith(
                      fontSize: 16,
                      color: currentValue - summary.investedAmount < 0
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
                  percentFormatter.format(
                      (summary.currentPrice * summary.amount) /
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
                  percentFormatter.format(
                      (summary.currentPrice * summary.amount) /
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
