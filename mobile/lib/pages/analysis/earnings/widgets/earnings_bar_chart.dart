import 'dart:io';

import 'package:charts_flutter/flutter.dart' as charts;
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/chart/stacked_bar_chart.dart';
import 'package:goatfolio/pages/portfolio/rgb.dart';
import 'package:goatfolio/services/performance/model/earnings_history.dart';
import 'package:goatfolio/utils/extensions.dart';
import 'package:goatfolio/utils/formatters.dart';
import 'package:intl/intl.dart';

class StockEarnings {
  final DateTime date;
  final double amount;

  StockEarnings(this.date, this.amount);
}

class EarningsBarChart extends StatefulWidget {
  final Future<List<charts.Series>> series;
  final Future<EarningsHistory> earningsHistory;

  const EarningsBarChart(
      {Key? key, required this.series, required this.earningsHistory})
      : super(key: key);

  @override
  _EarningsBarChart createState() => _EarningsBarChart();
}

class _EarningsBarChart extends State<EarningsBarChart> {
  final dateFormat = DateFormat('MMMM', 'pt_BR');
  EarningsDetails? selectedEarnings;

  final Map<String, Rgb> colors = Map();

  @override
  void initState() {
    widget.earningsHistory
        .then((value) => selectedEarnings = value.history.last);
    super.initState();
  }

  void onSelectionChanged(DateTime newSelection) async {
    selectedEarnings = (await widget.earningsHistory)
        .map[newSelection];
    setState(() {});
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
            'Valor recebido',
            style: textTheme.tabLabelTextStyle.copyWith(fontSize: 16),
          ),
          Text(
            selectedEarnings != null
                ? moneyFormatter.format(selectedEarnings!.total)
                : moneyFormatter.format(0),
            style: textTheme.textStyle
                .copyWith(fontSize: 28, fontWeight: FontWeight.w500),
          ),
          Text(
            selectedEarnings != null
                ? '${dateFormat.format(selectedEarnings!.date).capitalize()} de ${selectedEarnings!.date.year}'
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
      future: widget.series,
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
                        : Center(child: CircularProgressIndicator())),
              ],
            );
          case ConnectionState.done:
            if (snapshot.hasData) {
              final data =
                  snapshot.data as List<charts.Series<StockEarnings, DateTime>>;
              if (data.first.data.isEmpty || data.last.data.isEmpty) {
                return SizedBox(
                  height: 240,
                  child: Center(
                    child: Text("Nenhum gráfico disponivel."),
                  ),
                );
              }
              return Column(
                children: [
                  buildHeader(),
                  SizedBox(
                    height: 240,
                    child: StackedBarChart(
                      data,
                      onSelectionChanged: onSelectionChanged,
                    ),
                  ),
                  SizedBox(
                    height: 16,
                  ),
                  Expanded(
                    child: ListView.builder(
                      itemCount: selectedEarnings!.stocks.entries.length,
                      itemBuilder: (context, index) => Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Row(
                            children: [
                              Container(
                                width: 14,
                                height: 14,
                                color: colors.containsKey(selectedEarnings!
                                        .stocks.entries
                                        .toList()[index]
                                        .key)
                                    ? colors[selectedEarnings!.stocks.entries
                                            .toList()[index]
                                            .key]!
                                        .toColor()
                                    : Rgb.random().toColor(),
                              ),
                              Text(
                                ' ' +
                                    selectedEarnings!.stocks.entries
                                        .toList()[index]
                                        .key,
                                style: textTheme.textStyle,
                              ),
                            ],
                          ),
                          Text(
                              moneyFormatter.format(
                                selectedEarnings!.stocks.entries
                                    .toList()[index]
                                    .value,
                              ),
                              style: textTheme.textStyle
                                  .copyWith(fontWeight: FontWeight.w500)),
                        ],
                      ),
                    ),
                  )
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
        return Text("Erro ao carregar gráfico.");
      },
    );
  }
}
