import 'package:flutter/material.dart';
import 'package:charts_flutter/flutter.dart' as charts;

class LinearChart extends StatefulWidget {
  final List<charts.Series> seriesList;
  final bool animate;

  LinearChart(this.seriesList,
      {this.animate});

  @override
  _LinearChartState createState() => _LinearChartState();
}

class _LinearChartState extends State<LinearChart> {
  Widget _chart;

  @override
  Widget build(BuildContext context) {
    if (_chart == null) {
      _chart = _buildChart();
    }
    return _chart;

  }

  Widget _buildChart() {
    return Column(
      children: <Widget>[
        Expanded(
          child: new charts.TimeSeriesChart(
            widget.seriesList,
            animate: widget.animate,
            customSeriesRenderers: [
              new charts.SymbolAnnotationRendererConfig(
                  customRendererId: 'customSymbolAnnotation')
            ],
            dateTimeFactory: const charts.LocalDateTimeFactory(),
            primaryMeasureAxis: new charts.NumericAxisSpec(
              renderSpec: new charts.NoneRenderSpec(),
            ),
            domainAxis: new charts.DateTimeAxisSpec(
              showAxisLine: true,
              renderSpec: new charts.NoneRenderSpec(),
            ),
            behaviors: [
              new charts.SelectNearest(
                  eventTrigger: charts.SelectionTrigger.tapAndDrag),
            ],
            selectionModels: [
              new charts.SelectionModelConfig(
                type: charts.SelectionModelType.info,
                changedListener: (model) => 1,
              ),
            ],
          ),
        ),
      ],
    );
  }
}