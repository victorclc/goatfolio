import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:charts_flutter/flutter.dart' as charts;

class BarChart extends StatefulWidget {
  final List<charts.Series> seriesList;
  final bool animate;
  final Function onSelectionChanged;

  BarChart(this.seriesList, {this.onSelectionChanged, this.animate});

  @override
  _BarChartState createState() => _BarChartState();
}

class _BarChartState extends State<BarChart> {
  Widget _chart;

  @override
  Widget build(BuildContext context) {
    if (_chart == null) {
      _chart = _buildChart();
    }
    return _chart;
  }

  Widget _buildChart() {
    final textTheme = CupertinoTheme.of(context).textTheme;
    return Column(
      children: <Widget>[
        Expanded(
          child: new charts.BarChart(
            widget.seriesList,



            barGroupingType: charts.BarGroupingType.grouped,
            animate: widget.animate,
            customSeriesRenderers: [
              // new charts.LineRendererConfig(includeArea: true, stacked: true),
              new charts.SymbolAnnotationRendererConfig(
                  customRendererId: 'customSymbolAnnotation')
            ],
            domainAxis: new charts.OrdinalAxisSpec(
              renderSpec: new charts.NoneRenderSpec(),
              viewport: new charts.OrdinalViewport('04-21', 4),
            ),
            primaryMeasureAxis: new charts.NumericAxisSpec(
              renderSpec: new charts.GridlineRendererSpec(
                labelStyle: charts.TextStyleSpec(
                  fontFamily: textTheme.textStyle.fontFamily,
                  fontSize: 12,
                  fontWeight: textTheme.textStyle.fontWeight.toString(),
                  color:
                      charts.ColorUtil.fromDartColor(textTheme.textStyle.color),
                ),
              ),
            ),
            behaviors: [
              charts.SeriesLegend(
                  entryTextStyle: charts.TextStyleSpec(
                    fontFamily: textTheme.textStyle.fontFamily,
                    fontSize: 14,
                    fontWeight: textTheme.textStyle.fontWeight.toString(),
                    color: charts.ColorUtil.fromDartColor(
                        textTheme.textStyle.color),
                  ),
                  desiredMaxColumns: 2,
                  position: charts.BehaviorPosition.bottom),
              // new charts.SelectNearest(
              //     eventTrigger: charts.SelectionTrigger.tapAndDrag),
              charts.SlidingViewport(
                charts.SelectionModelType.action,
              ),
              charts.PanBehavior(),
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
