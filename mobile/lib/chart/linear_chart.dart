import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:charts_flutter/flutter.dart' as charts;

class LinearChart extends StatefulWidget {
  final List<charts.Series<dynamic, DateTime>> seriesList;
  final bool? animate;
  final Function onSelectionChanged;

  LinearChart(this.seriesList,
      {required this.onSelectionChanged, this.animate});

  @override
  _LinearChartState createState() => _LinearChartState();
}

class _LinearChartState extends State<LinearChart> {
  Widget? _chart;

  @override
  Widget build(BuildContext context) {
    if (_chart == null) {
      _chart = _buildChart();
    }
    return _chart!;
  }

  Widget _buildChart() {
    final textTheme = CupertinoTheme.of(context).textTheme;
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
              renderSpec: new charts.GridlineRendererSpec(
                labelStyle: charts.TextStyleSpec(
                  fontFamily: textTheme.textStyle.fontFamily,
                  fontSize: 12,
                  fontWeight: textTheme.textStyle.fontWeight.toString(),
                  color: charts.ColorUtil.fromDartColor(
                      textTheme.textStyle.color!),
                ),
              ),
            ),
            domainAxis: new charts.DateTimeAxisSpec(
              showAxisLine: true,
              renderSpec: new charts.NoneRenderSpec(),
            ),
            behaviors: [
              charts.SeriesLegend(
                  entryTextStyle: charts.TextStyleSpec(
                    fontFamily: textTheme.textStyle.fontFamily,
                    fontSize: 14,
                    fontWeight: textTheme.textStyle.fontWeight.toString(),
                    color: charts.ColorUtil.fromDartColor(
                        textTheme.textStyle.color!),
                  ),
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
                      result[element.series.displayName!] =
                          element.series.data[index!];
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
