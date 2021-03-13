import 'package:charts_flutter/flutter.dart' as charts;
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
    return new charts.PieChart(
      getSeries(),
      animate: widget.animate,
      selectionModels: [
        new charts.SelectionModelConfig(
          type: charts.SelectionModelType.info,
          changedListener: (model) {
            setState(() {
              tappedType = model.selectedDatum.first.datum.ticker;
              print(tappedType);
              stockTapped = !stockTapped;
              mustRebuild = true;
            });
          },
        ),
      ],
      defaultRenderer:
          new charts.ArcRendererConfig(arcWidth: 40, arcRendererDecorators: [
        new charts.ArcLabelDecorator(),
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
    if (chart == null || mustRebuild) {
      mustRebuild = false;
      chart = buildChart(context);
    }
    return chart;
  }
}