import 'dart:io';

import 'package:charts_flutter/flutter.dart' as charts;
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/pages/analysis/earnings/widgets/earnings_bar_chart.dart';
import 'package:goatfolio/pages/portfolio/rgb.dart';
import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:goatfolio/services/performance/client/performance_client.dart';
import 'package:goatfolio/services/performance/model/earnings_history.dart';
import 'package:goatfolio/utils/extensions.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

void goToEarningsPage(BuildContext context) {
  Navigator.of(context).push(
    MaterialPageRoute(
      builder: (context) => EarningsPage(),
    ),
  );
}

class EarningsPage extends StatefulWidget {
  final String title = "Proventos";

  const EarningsPage({Key? key}) : super(key: key);

  @override
  State<EarningsPage> createState() => _EarningsPageState();
}

class _EarningsPageState extends State<EarningsPage> {
  late final Future<EarningsHistory> _future;
  final Map<String, Rgb> colors = Map();

  @override
  void initState() {
    final userService = Provider.of<UserService>(context, listen: false);
    final client = PerformanceClient(userService);
    _future = client.getEarningsHistory();

    super.initState();
  }

  Future<List<charts.Series>> createChartSeries() async {
    final earningsHistory = await _future;
    earningsHistory.history
        .sort((a, b) => a.date.compareTo(b.date)); // tirar daqui

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
        series[ticker]!.add(
          StockEarnings(
              element.date, amount),
        );
      });
    });
    earningsHistory.colors = colors;
    List<charts.Series<StockEarnings, DateTime>> seriesList = [];
    series.forEach(
      (key, value) => seriesList.add(
        charts.Series<StockEarnings, DateTime>(
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

  @override
  Widget build(BuildContext context) {
    if (Platform.isIOS) {
      return buildIos(context);
    }
    return buildAndroid(context);
  }

  Widget buildAndroid(BuildContext context) {
    final textColor =
        CupertinoTheme.of(context).textTheme.navTitleTextStyle.color;
    return Scaffold(
      appBar: AppBar(
        leading: BackButton(
          color: textColor,
        ),
        title: Text(
          widget.title,
          style: TextStyle(color: textColor),
        ),
        backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
      ),
      backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
      body: _buildBody(context),
    );
  }

  Widget buildIos(BuildContext context) {
    return CupertinoPageScaffold(
      navigationBar: CupertinoNavigationBar(
        previousPageTitle: "",
        middle: Text(widget.title),
        backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
      ),
      child: _buildBody(context),
    );
  }

  Widget _buildBody(BuildContext context) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: EarningsBarChart(
          series: createChartSeries(),
          earningsHistory: _future,
        ),
      ),
    );
  }
}
