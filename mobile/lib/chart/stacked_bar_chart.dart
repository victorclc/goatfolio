import 'package:charts_flutter/flutter.dart' as charts;
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';

class StackedBarChart extends StatefulWidget {
  final List<charts.Series<dynamic, DateTime>> seriesList;
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
          child: new charts.TimeSeriesChart(
            widget.seriesList,
            defaultRenderer: new charts.BarRendererConfig<DateTime>(
              // barRendererDecorator: charts.BarLabelDecorator<DateTime>(),
              groupingType: charts.BarGroupingType.stacked,
              // strokeWidthPx: 1.0,
            ),
            defaultInteractions: false,
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
            domainAxis: new charts.DateTimeAxisSpec(
              viewport: charts.DateTimeExtents(
                start: DateTime(DateTime.now().year, DateTime.now().month - 5, 1),
                end: DateTime(DateTime.now().year, DateTime.now().month, 1),
              ),
              showAxisLine: false,
              renderSpec: charts.SmallTickRendererSpec(
                labelRotation: 30,
                labelStyle: charts.TextStyleSpec(
                  fontFamily: textTheme.textStyle.fontFamily,
                  fontSize: 12,
                  fontWeight: textTheme.textStyle.fontWeight.toString(),
                  color: charts.ColorUtil.fromDartColor(
                      textTheme.textStyle.color!),
                ),
              ),
            ),
            behaviors: [
              new charts.SlidingViewport(charts.SelectionModelType.info),
              new charts.PanAndZoomBehavior(),
              new charts.SelectNearest(
                  eventTrigger: charts.SelectionTrigger.tap),
              new charts.DomainHighlighter(),
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
