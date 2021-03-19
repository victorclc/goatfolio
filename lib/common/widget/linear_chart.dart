import 'package:flutter/material.dart';
import 'package:charts_flutter/flutter.dart' as charts;

class LinearChart extends StatefulWidget {
  final List<charts.Series> seriesList;
  final bool animate;
  final Function onSelectionChanged;

  LinearChart(this.seriesList, {this.onSelectionChanged, this.animate});

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
              charts.SeriesLegend(
                  desiredMaxColumns: 2,
                  position: charts.BehaviorPosition.bottom),
              new charts.SelectNearest(
                  eventTrigger: charts.SelectionTrigger.tapAndDrag),
            ],
            selectionModels: [
              new charts.SelectionModelConfig(
                type: charts.SelectionModelType.info,
                changedListener: (model) {
                  if (model.selectedDatum.isNotEmpty) {
                    final selectedDatum = model.selectedDatum;
                    final index = model.selectedDatum.first.index;
                    final Map<String, dynamic> result = Map();
                    selectedDatum.forEach((element) {
                      result[element.series.displayName] =
                          element.series.data[index];
                    });
                    widget.onSelectionChanged(result);
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
