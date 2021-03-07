import 'package:charts_flutter/flutter.dart' as charts;
import 'package:flutter/material.dart';

class DonutAutoLabelChart extends StatefulWidget {
  final List<charts.Series> investmentsList;
  final bool animate;

  DonutAutoLabelChart(this.investmentsList, {this.animate});

  @override
  _DonutAutoLabelChartState createState() => _DonutAutoLabelChartState();
}

class _DonutAutoLabelChartState extends State<DonutAutoLabelChart> {
  Widget chart;
  bool stockTapped = false;
  bool mustRebuild = false;
  String tappedType;

  @override
  Widget build(BuildContext context) {
    if (chart == null) {
      chart = new charts.PieChart(
        widget.investmentsList,
        animate: widget.animate,
        selectionModels: [
          new charts.SelectionModelConfig(
            type: charts.SelectionModelType.info,
          ),
        ],
        defaultRenderer:
            new charts.ArcRendererConfig(arcWidth: 40, arcRendererDecorators: [
          new charts.ArcLabelDecorator(),
        ]),
      );
    }
    return chart;
  }
}
