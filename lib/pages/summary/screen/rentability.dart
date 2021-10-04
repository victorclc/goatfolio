import 'dart:io';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/common/chart/money_date_series.dart';
import 'package:goatfolio/common/chart/valorization_chart.dart';
import 'package:goatfolio/common/formatter/brazil.dart';
import 'package:charts_flutter/flutter.dart' as charts;
import 'package:goatfolio/common/util/navigator.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/performance/client/performance_client.dart';
import 'package:goatfolio/services/performance/model/portfolio_history.dart';
import 'package:goatfolio/services/performance/model/portfolio_position.dart';
import 'package:goatfolio/services/performance/model/portfolio_summary.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

void goToRentabilityPage(BuildContext context, PortfolioSummary summary,
    UserService userService) async {
  await NavigatorUtils.push(
      context, (context) => RentabilityPage(summary, userService));
}

class RentabilityPage extends StatefulWidget {
  final PortfolioSummary summary;
  final UserService userService;

  const RentabilityPage(
    this.summary,
    this.userService, {
    Key key,
  }) : super(key: key);

  @override
  _RentabilityPageState createState() => _RentabilityPageState();
}

class _RentabilityPageState extends State<RentabilityPage> {
  final dateFormat = DateFormat('MMMM', 'pt_BR');
  PerformanceClient _client;
  String selectedTab;
  MoneyDateSeries selectedGrossSeries;
  MoneyDateSeries selectedInvestedSeries;
  Future<PortfolioHistory> _futureHistory;

  void initState() {
    super.initState();
    _client = PerformanceClient(widget.userService);
    _futureHistory = _client.getPortfolioRentabilityHistory();
    selectedTab = 'a';
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
          'Evolução',
          style: TextStyle(color: textColor),
        ),
        backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
      ),
      backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
      body: buildContent(context),
    );
  }

  Widget buildIos(BuildContext context) {
    return CupertinoPageScaffold(
      navigationBar: CupertinoNavigationBar(
        backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
        previousPageTitle: "",
        middle: Text('Evolução'),
      ),
      child: buildContent(context),
    );
  }

  Widget buildContent(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;

    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.only(left: 16, right: 16, top: 16),
        child: Column(
          children: [
            ValorizationChart(
              totalAmountSeries: createTotalAmountSeries(),
            ),
            Divider(
              color: Colors.grey,
              height: 24,
            ),
            Container(
              alignment: Alignment.centerLeft,
              child: Text(
                "Mais informações",
                style: textTheme.navTitleTextStyle,
              ),
            ),
            SizedBox(
              height: 16,
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Saldo bruto', style: textTheme.textStyle),
                Text(moneyFormatter.format(widget.summary.grossAmount),
                    style: textTheme.textStyle),
              ],
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Valor investido', style: textTheme.textStyle),
                Text(moneyFormatter.format(widget.summary.investedAmount),
                    style: textTheme.textStyle),
              ],
            ),
            SizedBox(
              height: 4,
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Resultado', style: textTheme.textStyle),
                Text(
                  moneyFormatter.format(widget.summary.grossAmount -
                      widget.summary.investedAmount),
                  style: textTheme.textStyle.copyWith(
                      color: widget.summary.grossAmount -
                                  widget.summary.investedAmount >=
                              0
                          ? Colors.green
                          : Colors.red),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }


  Future<List<charts.Series<MoneyDateSeries, DateTime>>>
      createTotalAmountSeries() async {
    // TODO CHANGE THIS TO PORTFOLIO HISTORY CLASS
    PortfolioHistory portfolioHistory = await _futureHistory;
    List<MoneyDateSeries> seriesGross = [];
    List<MoneyDateSeries> seriesInvested = [];

    portfolioHistory.history.sort((a, b) => a.date.compareTo(b.date));

    portfolioHistory.history.forEach((element) {
      seriesInvested.add(MoneyDateSeries(element.date, element.investedValue));
      seriesGross.add(MoneyDateSeries(element.date, element.grossValue));
    });

    return [
      new charts.Series<MoneyDateSeries, DateTime>(
        id: "Saldo bruto",
        colorFn: (_, __) => charts.MaterialPalette.blue.shadeDefault,
        domainFn: (MoneyDateSeries history, _) => history.date,
        areaColorFn: (_, __) =>
            charts.MaterialPalette.blue.shadeDefault.lighter,
        measureFn: (MoneyDateSeries history, _) => history.money,
        data: seriesGross,
      ),
      new charts.Series<MoneyDateSeries, DateTime>(
        id: "Valor investido",
        colorFn: (_, __) => charts.MaterialPalette.deepOrange.shadeDefault,
        domainFn: (MoneyDateSeries history, _) => history.date,
        dashPatternFn: (_, __) => [2, 2],
        measureFn: (MoneyDateSeries history, _) => history.money,
        data: seriesInvested,
      ),
    ];
  }
}
