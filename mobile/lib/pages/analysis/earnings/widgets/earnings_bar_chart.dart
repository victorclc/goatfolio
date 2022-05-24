import 'dart:io';

import 'package:charts_flutter/flutter.dart' as charts;
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/chart/stacked_bar_chart.dart';
import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:goatfolio/services/performance/client/performance_client.dart';
import 'package:goatfolio/services/performance/model/earnings_history.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

class StockEarnings {
  final String date;
  final double amount;

  StockEarnings(this.date, this.amount);
}

class EarningsBarChart extends StatefulWidget {
  final EarningsHistory earningsHistory;

  const EarningsBarChart({
    Key? key,
    required this.earningsHistory,
  }) : super(key: key);

  @override
  _EarningsBarChart createState() => _EarningsBarChart();
}

class _EarningsBarChart extends State<EarningsBarChart> {
  final dateFormat = DateFormat('MMMM', 'pt_BR');
  late final PerformanceClient _client;

  @override
  void initState() {
    // TODO isso daqui ja tem q vir ordenado tirar daqui
    final userService = Provider.of<UserService>(context, listen: false);
    _client = PerformanceClient(userService);
    super.initState();
  }

  Future<List<charts.Series>> createChartSeries(
      EarningsHistory earningsHistory) async {
    earningsHistory = await _client.getEarningsHistory();
    earningsHistory.history.sort((a, b) => a.date.compareTo(b.date));

    Map<String, List<StockEarnings>> series = {};
    earningsHistory.history.forEach((element) {
      element.stocks.entries.forEach((stock) {
        final ticker = stock.key;
        final amount = stock.value;
        if (!series.containsKey(ticker)) {
          series[ticker] = [];
        }
        series[ticker]!.add(
            StockEarnings(DateFormat("MMM yyyy").format(element.date), amount));
      });
    });

    List<charts.Series<StockEarnings, String>> seriesList = [];

    series.forEach(
      (key, value) => seriesList.add(
        charts.Series<StockEarnings, String>(
            id: key,
            data: value,
            domainFn: (StockEarnings s, _) => s.date,
            measureFn: (StockEarnings s, _) => s.amount),
      ),
    );

    return seriesList;
  }

  void onSelectionChanged(Map<String, dynamic> series) {
    print(series);
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
            'Saldo bruto',
            style: textTheme.tabLabelTextStyle.copyWith(fontSize: 16),
          ),
          // Text(
          //   selectedGrossSeries != null
          //       ? moneyFormatter.format(selectedGrossSeries!.money)
          //       : moneyFormatter.format(0),
          //   style: textTheme.textStyle
          //       .copyWith(fontSize: 28, fontWeight: FontWeight.w500),
          // ),
          Text(
            'Valor investido',
            style: textTheme.tabLabelTextStyle.copyWith(fontSize: 16),
          ),
          // Text(
          //   selectedInvestedSeries != null
          //       ? moneyFormatter.format(selectedInvestedSeries!.money)
          //       : moneyFormatter.format(0),
          //   style: textTheme.textStyle
          //       .copyWith(fontSize: 20, fontWeight: FontWeight.w500),
          // ),
          // Text(
          //   selectedGrossSeries != null
          //       ? '${dateFormat.format(selectedGrossSeries!.date).capitalize()} de ${selectedGrossSeries!.date.year}'
          //       : '${dateFormat.format(DateTime.now()).capitalize()} de ${DateTime.now().year}',
          //   style: textTheme.tabLabelTextStyle
          //       .copyWith(fontSize: 16, fontWeight: FontWeight.w400),
          // ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;

    return FutureBuilder(
      future: createChartSeries(widget.earningsHistory),
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
