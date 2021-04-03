import 'package:charts_flutter/flutter.dart' as charts;
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';

class DonutAutoLabelChart extends StatefulWidget {
  final List<charts.Series> typeSeries;
  final List<charts.Series> stocksSeries;
  final List<charts.Series> reitsSeries;
  final bool animate;

  DonutAutoLabelChart(
      {this.animate, this.typeSeries, this.stocksSeries, this.reitsSeries});

  @override
  _DonutAutoLabelChartState createState() => _DonutAutoLabelChartState();
}

class _DonutAutoLabelChartState extends State<DonutAutoLabelChart> {
  Widget chart;
  bool stockTapped = false;
  bool mustRebuild = false;
  String tappedType;

  Widget buildChart(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;
    final fontcolor = textTheme.textStyle.color;
    return new charts.PieChart(
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
                r: fontcolor.red,
                g: fontcolor.green,
                b: fontcolor.blue,
                a: fontcolor.alpha),
          ),
        )
      ]),
    );
  }

  List<charts.Series> getSeries() {
    if (!stockTapped) {
      return widget.typeSeries;
    }
    return 'FIIs' == tappedType ? widget.reitsSeries : widget.stocksSeries;
  }

  @override
  Widget build(BuildContext context) {
    if (widget.typeSeries.first.data.isEmpty) {
      return Center(
        child: Text("Nenhum dado ainda.",
            style: CupertinoTheme.of(context).textTheme.textStyle),
      );
    }
    if (chart == null || mustRebuild) {
      mustRebuild = false;
      chart = buildChart(context);
    }
    return chart;
  }
}
