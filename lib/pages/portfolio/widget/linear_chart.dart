import 'package:flutter/material.dart';
import 'package:charts_flutter/flutter.dart' as charts;

class LinearChartChart extends StatefulWidget {
  final List<charts.Series> seriesList;
  final bool animate;
  final Function onSelectionChanged;

  LinearChartChart(this.seriesList, {this.onSelectionChanged, this.animate});

  @override
  _LinearChartChartState createState() => _LinearChartChartState();
}

class _LinearChartChartState extends State<LinearChartChart> {
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
              // new charts.LineRendererConfig(includeArea: true, stacked: true),
              new charts.SymbolAnnotationRendererConfig(
                  customRendererId: 'customSymbolAnnotation')
            ],
            dateTimeFactory: const charts.LocalDateTimeFactory(),
            primaryMeasureAxis: new charts.NumericAxisSpec(
                // renderSpec: new charts.NoneRenderSpec(),
                ),
            domainAxis: new charts.DateTimeAxisSpec(
              showAxisLine: true,
              renderSpec: new charts.NoneRenderSpec(),
            ),
            behaviors: [
              charts.SeriesLegend(desiredMaxColumns: 2, position: charts.BehaviorPosition.bottom),
              new charts.SelectNearest(
                  eventTrigger: charts.SelectionTrigger.tapAndDrag),
            ],
            selectionModels: [
              new charts.SelectionModelConfig(
                type: charts.SelectionModelType.info,
                changedListener: (model) {
                  if (model.selectedDatum.isNotEmpty) {
                    final selectedDatum = model.selectedDatum.first.series.data;
                    final index = model.selectedDatum.first.index;
                    widget.onSelectionChanged(selectedDatum[index]);
                  }
                },
              ),
            ],
          ),
        ),
      ],
    );
  }
}
