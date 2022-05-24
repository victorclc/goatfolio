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
              // strokeWidthPx: 1.0,
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
                viewport: new charts.OrdinalViewport(widget.seriesList.last.data.last.date, 6),
                showAxisLine: false,renderSpec:  charts.SmallTickRendererSpec(labelRotation: 30, labelStyle: charts.TextStyleSpec(
              fontFamily: textTheme.textStyle.fontFamily,
              fontSize: 12,
              fontWeight: textTheme.textStyle.fontWeight.toString(),
              color: charts.ColorUtil.fromDartColor(
                  textTheme.textStyle.color!),
            ),)
            ),
            behaviors: [
              new charts.PanAndZoomBehavior(),
              new charts.SelectNearest(
                  eventTrigger: charts.SelectionTrigger.tap),
            ],
            selectionModels: [
              new charts.SelectionModelConfig(
                type: charts.SelectionModelType.info,
                changedListener: (model) {
                  if (model.selectedDatum.isNotEmpty) {
                    final selectedDatum = model.selectedDatum;
                    widget.onSelectionChanged(selectedDatum.first.datum.date);
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
