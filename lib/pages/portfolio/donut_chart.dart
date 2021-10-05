import 'package:charts_flutter/flutter.dart' as charts;
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/pages/portfolio/ticker_totals.dart';
import 'package:goatfolio/performance/model/portfolio_performance.dart';
import 'package:goatfolio/theme/theme_changer.dart';

import 'package:provider/provider.dart';

class DonutAutoLabelChart extends StatefulWidget {
  final PortfolioPerformance? portfolioList;
  final List<charts.Series<TickerTotals, String>>? typeSeries;
  final List<charts.Series<TickerTotals, String>>? stocksSeries;
  final List<charts.Series<TickerTotals, String>>? reitsSeries;
  final List<charts.Series<TickerTotals, String>>? bdrsSeries;
  final bool? animate;

  DonutAutoLabelChart(
      {this.animate,
      this.typeSeries,
      this.stocksSeries,
      this.reitsSeries,
      this.bdrsSeries,
      this.portfolioList});

  @override
  _DonutAutoLabelChartState createState() => _DonutAutoLabelChartState();
}

class _DonutAutoLabelChartState extends State<DonutAutoLabelChart> {
  Widget? chart;
  bool stockTapped = false;
  bool mustRebuild = false;
  String? tappedType;
  double? grossAmount;
  CupertinoThemeData? _previousTheme;

  void initState() {
    super.initState();
    grossAmount = widget.portfolioList!.grossValue;
  }

  Widget buildChart(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;
    final fontcolor = textTheme.textStyle.color;
    return new charts.PieChart<String>(
      getSeries(),
      animate: widget.animate,
      selectionModels: [
        new charts.SelectionModelConfig(
          type: charts.SelectionModelType.info,
          changedListener: (model) {
            setState(() {
              tappedType = model.selectedDatum.first.datum.ticker;
              stockTapped = !stockTapped;
              mustRebuild = true;
            });
          },
        ),
      ],
      defaultRenderer:
          new charts.ArcRendererConfig(arcWidth: 40, arcRendererDecorators: [
        new charts.ArcLabelDecorator(
          insideLabelStyleSpec: charts.TextStyleSpec(
              fontSize: 14,
              fontFamily: textTheme.textStyle.fontFamily,
              fontWeight: textTheme.textStyle.fontWeight.toString(),
              color: charts.MaterialPalette.white),
          outsideLabelStyleSpec: charts.TextStyleSpec(
            fontSize: 14,
            fontFamily: textTheme.textStyle.fontFamily,
            color: charts.Color(
                r: fontcolor!.red,
                g: fontcolor.green,
                b: fontcolor.blue,
                a: fontcolor.alpha),
          ),
        )
      ]),
    );
  }

  List<charts.Series<TickerTotals, String>> getSeries() {
    if (!stockTapped) {
      return widget.typeSeries!;
    }
    switch (tappedType) {
      case 'FIIs':
        return widget.reitsSeries!;
      case 'BDRs':
        return widget.bdrsSeries!;
      default:
        return widget.stocksSeries!;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<ThemeChanger>(builder: (context, theme, _) {
      if (_previousTheme != null && _previousTheme != theme.themeData) {
        mustRebuild = true;
      }
      _previousTheme = theme.themeData;
      if (widget.typeSeries!.first.data.isEmpty) {
        return Center(
          child: Text("Nenhum dado ainda.",
              style: CupertinoTheme.of(context).textTheme.textStyle),
        );
      }
      if (chart == null ||
          mustRebuild ||
          grossAmount != widget.portfolioList!.grossValue) {
        grossAmount = widget.portfolioList!.grossValue;
        mustRebuild = false;
        chart = buildChart(context);
      }
      return chart!;
    });
  }
}
