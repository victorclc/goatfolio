import 'package:charts_flutter/flutter.dart' as charts;
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';

class StackedBarChart extends StatefulWidget {
  final List<charts.Series<dynamic, String>> seriesList;
  final bool? animate;
  final Function onSelectionChanged;

  StackedBarChart(this.seriesList,
      {required this.onSelectionChanged, this.animate});

  @override
  _StackedBarChart createState() => _StackedBarChart();
}

class _StackedBarChart extends State<StackedBarChart> {
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
          child: new charts.BarChart(
            widget.seriesList,
            defaultRenderer: new charts.BarRendererConfig(
              groupingType: charts.BarGroupingType.stacked,
              strokeWidthPx: 2.0,

            ),
            animate: widget.animate,
            customSeriesRenderers: [
              // new charts.LineRendererConfig(includeArea: true, stacked: true),
              new charts.SymbolAnnotationRendererConfig(
                  customRendererId: 'customSymbolAnnotation')
            ],
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
            domainAxis: new charts.OrdinalAxisSpec(
                viewport: new charts.OrdinalViewport("Dec 2023", 5),showAxisLine: false
                ),
            behaviors: [
              // charts.SeriesLegend(
              //     entryTextStyle: charts.TextStyleSpec(
              //       fontFamily: textTheme.textStyle.fontFamily,
              //       fontSize: 14,
              //       fontWeight: textTheme.textStyle.fontWeight.toString(),
              //       color: charts.ColorUtil.fromDartColor(
              //           textTheme.textStyle.color!),
              //     ),
              //     desiredMaxColumns: 2,
              //     position: charts.BehaviorPosition.bottom),
              new charts.PanAndZoomBehavior(),
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
