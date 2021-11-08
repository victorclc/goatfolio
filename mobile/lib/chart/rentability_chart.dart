import 'dart:io';

import 'package:flutter/cupertino.dart';
import 'package:charts_flutter/flutter.dart' as charts;
import 'package:flutter/material.dart';
import 'package:goatfolio/chart/linear_chart.dart';
import 'package:goatfolio/utils/extensions.dart';
import 'package:goatfolio/utils/formatters.dart';

import 'package:intl/intl.dart';

import 'money_date_series.dart';

class RentabilityChart extends StatefulWidget {
  final Future<List<charts.Series>> rentabilitySeries;

  const RentabilityChart({Key? key, required this.rentabilitySeries})
      : super(key: key);

  @override
  _RentabilityChartState createState() => _RentabilityChartState();
}

class _RentabilityChartState extends State<RentabilityChart> {
  MoneyDateSeries? selectedGrossSeries;
  MoneyDateSeries? selectedIbovSeries;
  final dateFormat = DateFormat('MMMM', 'pt_BR');

  @override
  void initState() {
    super.initState();
  }

  void onSelectionChanged(Map<String, dynamic> series) {
    setState(() {
      selectedGrossSeries = series['Rentabilidade'];
      selectedIbovSeries = series['IBOV'];
    });
  }

  Widget buildHeader() {
    final textTheme = CupertinoTheme.of(context).textTheme;
    return Container(
      padding: EdgeInsets.only(top: 4),
      alignment: Alignment.centerLeft,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Rentabilidade',
            style: textTheme.tabLabelTextStyle.copyWith(fontSize: 16),
          ),
          Text(
            selectedGrossSeries != null
                ? percentFormatter.format(selectedGrossSeries!.money / 100)
                : percentFormatter.format(0),
            style: textTheme.textStyle
                .copyWith(fontSize: 28, fontWeight: FontWeight.w500),
          ),
          Text(
            'Ibovespa',
            style: textTheme.tabLabelTextStyle.copyWith(fontSize: 16),
          ),
          Text(
            selectedIbovSeries != null
                ? percentFormatter.format(selectedIbovSeries!.money / 100)
                : percentFormatter.format(0),
            style: textTheme.textStyle
                .copyWith(fontSize: 20, fontWeight: FontWeight.w500),
          ),
          Text(
            selectedGrossSeries != null
                ? '${dateFormat.format(selectedGrossSeries!.date).capitalize()} de ${selectedGrossSeries!.date.year}'
                : '${dateFormat.format(DateTime.now()).capitalize()} de ${DateTime.now().year}',
            style: textTheme.tabLabelTextStyle
                .copyWith(fontSize: 16, fontWeight: FontWeight.w400),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;

    return FutureBuilder(
      future: widget.rentabilitySeries,
      builder: (context, snapshot) {
        switch (snapshot.connectionState) {
          case ConnectionState.none:
          case ConnectionState.active:
            break;
          case ConnectionState.waiting:
            return Column(
              children: [
                buildHeader(),
                SizedBox(
                  height: 240,
                  child: Platform.isIOS
                      ? CupertinoActivityIndicator()
                      : Center(child: CircularProgressIndicator()),
                ),
              ],
            );
          case ConnectionState.done:
            if (snapshot.hasData) {
              final data =
                  snapshot.data! as List<charts.Series<dynamic, DateTime>>;
              if (data.first.data.isEmpty || data.last.data.isEmpty) {
                return SizedBox(
                    height: 240,
                    child: Center(child: Text("Grafico indisponivel.")));
              }
              if (selectedGrossSeries == null) {
                selectedGrossSeries = data.first.data.last;
              }
              if (selectedIbovSeries == null) {
                selectedIbovSeries = data.last.data.last;
              }
              return Column(
                children: [
                  buildHeader(),
                  SizedBox(
                    height: 240,
                    child: LinearChart(
                      data,
                      onSelectionChanged: onSelectionChanged,
                    ),
                  ),
                ],
              );
            } else {
              return Column(
                children: [
                  buildHeader(),
                  SizedBox(
                    height: 240,
                    child: Center(
                      child: Text(
                        "Nenhum dado ainda.",
                        style: textTheme.textStyle,
                      ),
                    ),
                  ),
                ],
              );
            }
        }
        return Text("deu algum erro");
      },
    );
  }
}
