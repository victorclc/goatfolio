import 'dart:io';

import 'package:charts_flutter/flutter.dart' as charts;
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/chart/stacked_bar_chart.dart';
import 'package:goatfolio/pages/portfolio/rgb.dart';
import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:goatfolio/services/performance/client/performance_client.dart';
import 'package:goatfolio/services/performance/model/earnings_history.dart';
import 'package:goatfolio/utils/extensions.dart';
import 'package:goatfolio/utils/formatters.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

class StockEarnings {
  final String date;
  final double amount;

  StockEarnings(this.date, this.amount);
}

class EarningsBarChart extends StatefulWidget {
  EarningsHistory earningsHistory;

  EarningsBarChart({
    Key? key,
    required this.earningsHistory,
  }) : super(key: key);

  @override
  _EarningsBarChart createState() => _EarningsBarChart();
}

class _EarningsBarChart extends State<EarningsBarChart> {
  final dateFormat = DateFormat('MMMM', 'pt_BR');
  EarningsDetails? selectedEarnings;
  late final PerformanceClient _client;
  late final Future<List<charts.Series>> _future;
  final Map<String, Rgb> colors = Map();

  @override
  void initState() {
    final userService = Provider.of<UserService>(context, listen: false);
    _client = PerformanceClient(userService);
    _future = createChartSeries(widget.earningsHistory);
    super.initState();
  }

  Future<List<charts.Series>> createChartSeries(
      EarningsHistory earningsHistory) async {
    earningsHistory = await _client.getEarningsHistory();
    earningsHistory.history.sort((a, b) => a.date.compareTo(b.date));
    widget.earningsHistory = earningsHistory;
    selectedEarnings = earningsHistory.history.last;

    Map<String, List<StockEarnings>> series = {};
    earningsHistory.history.forEach((element) {
      element.stocks.entries.forEach((stock) {
        final ticker = stock.key;
        final amount = stock.value;
        if (!series.containsKey(ticker)) {
          series[ticker] = [];
        }
        if (!colors.containsKey(ticker)) {
          colors[ticker] = Rgb.random();
        }
        series[ticker]!.add(StockEarnings(
            DateFormat("MMM yyyy", "pt-BR")
                .format(element.date)
                .capitalizeWords(),
            amount));
      });
    });

    List<charts.Series<StockEarnings, String>> seriesList = [];

    series.forEach(
      (key, value) => seriesList.add(
        charts.Series<StockEarnings, String>(
            id: key,
            data: value,
            colorFn: (_, __) =>
                charts.ColorUtil.fromDartColor(colors[key]!.toColor()),
            domainFn: (StockEarnings s, _) => s.date,
            measureFn: (StockEarnings s, _) => s.amount),
      ),
    );
    return seriesList;
  }

  void onSelectionChanged(String newSelection) {
    selectedEarnings = widget.earningsHistory
        .map[DateFormat("MMM yyyy", "pt-BR").parse(newSelection.toLowerCase())];
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
      future: _future,
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
                  snapshot.data as List<charts.Series<StockEarnings, String>>;
              if (data.first.data.isEmpty || data.last.data.isEmpty) {
                return SizedBox(
                  height: 240,
                  child: Center(
                    child: Text("Nenhum gráfico disponivel."),
                  ),
                );
              }
              // if (selectedGrossSeries == null) {
              //   selectedGrossSeries = data.first.data.last;
              // }
              // if (selectedInvestedSeries == null) {
              //   selectedInvestedSeries = data.last.data.last;
              // }
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
