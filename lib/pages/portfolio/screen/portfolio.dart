import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:goatfolio/common/bloc/loading/loading_state.dart';
import 'package:goatfolio/common/widget/cupertino_sliver_page.dart';
import 'package:goatfolio/common/widget/loading_error.dart';
import 'package:goatfolio/common/widget/platform_aware_progress_indicator.dart';
import 'package:goatfolio/pages/portfolio/model/rgb.dart';
import 'package:goatfolio/pages/portfolio/model/ticker_totals.dart';
import 'package:goatfolio/pages/portfolio/widget/donut_chart.dart';
import 'package:goatfolio/pages/portfolio/widget/investment_type_expansion_tile.dart';
import 'package:goatfolio/services/performance/cubit/performance_cubit.dart';
import 'package:goatfolio/services/performance/model/portfolio_performance.dart';

import 'package:charts_flutter/flutter.dart' as charts;

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
              } else if (state == LoadingState.LOADED ||
                  cubit.portfolioPerformance != null) {
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
                        stocksSeries: cubit.portfolioPerformance.hasStocks
                            ? buildSeries(
                                'stocks',
                                cubit.portfolioPerformance.stockSummary
                                    .openedPositions,
                              )
                            : null,
                        reitsSeries: cubit.portfolioPerformance.hasReits
                            ? buildSeries(
                                'reits',
                                cubit.portfolioPerformance.reitSummary
                                    .openedPositions,
                              )
                            : null,
                        bdrsSeries: cubit.portfolioPerformance.hasBdrs
                            ? buildSeries(
                                'bdrs',
                                cubit.portfolioPerformance.bdrSummary
                                    .openedPositions)
                            : null,
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
                    if (cubit.portfolioPerformance.hasStocks)
                      InvestmentTypeExpansionTile(
                        title: 'Ações/ETFs',
                        grossAmount: cubit.portfolioPerformance.stockSummary.grossValue,
                        items: cubit.portfolioPerformance.stockSummary.openedPositions,
                        colors: colors,
                        totalAmount: cubit.portfolioPerformance.grossValue,
                      ),
                    if (cubit.portfolioPerformance.hasBdrs)
                      InvestmentTypeExpansionTile(
                        title: 'BDRs',
                        grossAmount: cubit.portfolioPerformance.bdrSummary.grossValue,
                        items: cubit.portfolioPerformance.bdrSummary.openedPositions,
                        colors: colors,
                        totalAmount: cubit.portfolioPerformance.grossValue,
                      ),
                    if (cubit.portfolioPerformance.hasReits)
                      InvestmentTypeExpansionTile(
                        title: 'FIIs',
                        grossAmount: cubit.portfolioPerformance.reitSummary.grossValue,
                        items: cubit.portfolioPerformance.reitSummary.openedPositions,
                        colors: colors,
                        totalAmount: cubit.portfolioPerformance.grossValue,
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

  List<charts.Series<TickerTotals, String>> buildSeries(
      String id, List stocks) {
    List<TickerTotals> data = stocks.map((p) {
      final color = Rgb.random();
      colors[p.ticker] = color;
      if (p.quantity <= 0) {
        return null;
      }
      return TickerTotals(p.currentTickerName, p.grossValue, color);
    }).toList()
      ..removeWhere((element) => element == null);
    return [
      new charts.Series<TickerTotals, String>(
        id: id,
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
    if (performance.hasStocks && performance.stockSummary.grossValue > 0) {
      colors['Ações/ETFs'] =
          Rgb(stockColor.red, stockColor.green, stockColor.blue);
      data.add(TickerTotals('Ações\ne ETFs',
          performance.stockSummary.grossValue, colors['Ações/ETFs']));
    }
    final reitColor = Color(0xf52d6f);
    if (performance.hasReits && performance.reitSummary.grossValue > 0) {
      colors['FIIs'] = Rgb(reitColor.red, reitColor.green, reitColor.blue);
      data.add(TickerTotals(
          'FIIs', performance.reitSummary.grossValue, colors['FIIs']));
    }

    final bdrColor = Color(0xffa514);
    if (performance.hasBdrs && performance.bdrSummary.grossValue > 0) {
      colors['BDRs'] = Rgb(bdrColor.red, bdrColor.green, bdrColor.blue);
      data.add(TickerTotals(
          'BDRs', performance.bdrSummary.grossValue, colors['BDRs']));
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
