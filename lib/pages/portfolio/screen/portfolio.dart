import 'dart:io';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:goatfolio/common/bloc/loading/loading_state.dart';
import 'package:goatfolio/common/formatter/brazil.dart';
import 'package:goatfolio/common/widget/cupertino_sliver_page.dart';
import 'package:goatfolio/common/widget/expansion_tile_custom.dart';
import 'package:goatfolio/common/widget/loading_error.dart';
import 'package:goatfolio/common/widget/platform_aware_progress_indicator.dart';
import 'package:goatfolio/pages/portfolio/widget/donut_chart.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/performance/cubit/performance_cubit.dart';
import 'package:goatfolio/services/performance/model/benchmark_position.dart';
import 'package:goatfolio/services/performance/model/portfolio_performance.dart';
import 'package:goatfolio/services/performance/model/stock_summary.dart';
import 'package:provider/provider.dart';

import 'dart:math' as math;
import 'package:charts_flutter/flutter.dart' as charts;

import 'investment_details.dart';

class PortfolioPage extends StatelessWidget {
  static const title = 'Portfolio';
  static const icon = Icon(Icons.trending_up);
  final Map<String, Rgb> colors = Map();

  @override
  Widget build(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;
    return BlocBuilder<PerformanceCubit, LoadingState>(
        builder: (context, state) {
      final cubit = BlocProvider.of<PerformanceCubit>(context);

      return CupertinoSliverPage(
        largeTitle: PortfolioPage.title,
        children: [
          Builder(
            builder: (_) {
              if (state == LoadingState.LOADING &&
                  cubit.portfolioPerformance == null) {
                return PlatformAwareProgressIndicator();
              } else if (state == LoadingState.LOADED) {
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
                          portfolioList: cubit.portfolioPerformance,
                          typeSeries:
                              buildSubtypeSeries(cubit.portfolioPerformance),
                          stocksSeries: buildStockSeries(
                              cubit.portfolioPerformance.stocks),
                          reitsSeries:
                              buildReitSeries(cubit.portfolioPerformance.reits),
                          bdrsSeries:
                              buildBdrSeries(cubit.portfolioPerformance.bdrs)),
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
                      grossAmount: cubit.portfolioPerformance.stockGrossAmount,
                      items: cubit.portfolioPerformance.stocks,
                      colors: colors,
                      totalAmount: cubit.portfolioPerformance.grossAmount,
                      ibovHistory: cubit.portfolioPerformance.ibovHistory,
                    ),
                    InvestmentTypeExpansionTile(
                      title: 'BDRs',
                      grossAmount: cubit.portfolioPerformance.bdrGrossAmount,
                      items: cubit.portfolioPerformance.bdrs,
                      colors: colors,
                      totalAmount: cubit.portfolioPerformance.grossAmount,
                      ibovHistory: cubit.portfolioPerformance.ibovHistory,
                    ),
                    InvestmentTypeExpansionTile(
                      title: 'FIIs',
                      grossAmount: cubit.portfolioPerformance.reitGrossAmount,
                      items: cubit.portfolioPerformance.reits,
                      colors: colors,
                      totalAmount: cubit.portfolioPerformance.grossAmount,
                      ibovHistory: cubit.portfolioPerformance.ibovHistory,
                    ),
                  ],
                );
              } else {
                return LoadingError(onRefreshPressed: cubit.refresh);
              }
            },
          ),
        ],
      );
    });
  }

  List<charts.Series<TickerTotals, String>> buildStockSeries(List stocks) {
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

  List<charts.Series<TickerTotals, String>> buildReitSeries(List reits) {
    List<TickerTotals> data = reits.map((p) {
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

  List<charts.Series<TickerTotals, String>> buildBdrSeries(List bdrs) {
    List<TickerTotals> data = bdrs.map((p) {
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

  List<charts.Series<TickerTotals, String>> buildSubtypeSeries(
      PortfolioPerformance performance) {
    List<TickerTotals> data = [];

    // #5c36ad
    // #ec1a72
    // #ff8c12
    final stockColor = Color(0x5c36ad);
    if (performance.stockGrossAmount > 0) {
      colors['Ações/ETFs'] =
          Rgb(stockColor.red, stockColor.green, stockColor.blue);
      data.add(TickerTotals(
          'Ações\ne ETFs', performance.stockGrossAmount, colors['Ações/ETFs']));
    }
    final reitColor = Color(0xf52d6f);
    if (performance.reitGrossAmount > 0) {
      colors['FIIs'] = Rgb(reitColor.red, reitColor.green, reitColor.blue);
      data.add(
          TickerTotals('FIIs', performance.reitGrossAmount, colors['FIIs']));
    }

    final bdrColor = Color(0xffa514);
    if (performance.bdrGrossAmount > 0) {
      colors['BDRs'] = Rgb(bdrColor.red, bdrColor.green, bdrColor.blue);
      data.add(
          TickerTotals('BDRs', performance.reitGrossAmount, colors['BDRs']));
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
