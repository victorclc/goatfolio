import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/common/chart/money_date_series.dart';
import 'package:goatfolio/common/chart/valorization_chart.dart';
import 'package:goatfolio/common/formatter/brazil.dart';
import 'package:charts_flutter/flutter.dart' as charts;
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/performance/client/performance_client.dart';
import 'package:goatfolio/services/performance/model/portfolio_history.dart';
import 'package:goatfolio/services/performance/model/portfolio_position.dart';
import 'package:goatfolio/services/performance/model/portfolio_summary.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

void goToRentabilityPage(BuildContext context, PortfolioSummary summary) async {
  await Navigator.push(
    context,
    CupertinoPageRoute(
      builder: (context) => RentabilityPage(summary),
    ),
  );
}

class RentabilityPage extends StatefulWidget {
  final PortfolioSummary summary;

  const RentabilityPage(this.summary, {Key key}) : super(key: key);

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
    final userService = Provider.of<UserService>(context, listen: false);
    _client = PerformanceClient(userService);
    _futureHistory = _client.getPortfolioRentabilityHistory();
    selectedTab = 'a';
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;
    return CupertinoPageScaffold(
      navigationBar: CupertinoNavigationBar(
        backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
        previousPageTitle: "",
        middle: Text('Evolução'),
      ),
      child: SafeArea(
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
      ),
    );
  }

  Future<List<charts.Series<MoneyDateSeries, String>>>
      createRentabilitySeries() async {
    PortfolioHistory portfolioHistory = await _futureHistory;
    List<MoneyDateSeries> series = [];
    portfolioHistory.history.sort((a, b) => a.date.compareTo(b.date));
    double prevMonthTotal = 0.0;
    double acumulatedRentability = 0.0;

    for (PortfolioPosition element in portfolioHistory.history) {
      final monthTotal = element.grossValue;
      acumulatedRentability =
          ((monthTotal) / (prevMonthTotal + element.investedValue) - 1) * 100;
      prevMonthTotal = monthTotal;
      series.add(MoneyDateSeries(element.date, acumulatedRentability));
    }
    final now = DateTime.now();
    acumulatedRentability +=
        (widget.summary.grossAmount / prevMonthTotal - 1) * 100;
    series.add(MoneyDateSeries(
        DateTime(now.year, now.month, 1), acumulatedRentability));

    List<MoneyDateSeries> ibovSeries = [];
    portfolioHistory.ibovHistory.sort((a, b) => a.date.compareTo(b.date));
    prevMonthTotal = 0.0;
    acumulatedRentability = 0.0;
    portfolioHistory.ibovHistory.forEach((element) {
      // if (element.date.year < widget.performance.initialDate.year ||
      //     element.date.year == widget.performance.initialDate.year &&
      //         element.date.month < widget.performance.initialDate.month)
      //   print("data antiga");
      // else {
      //   print('data nova');
      if (prevMonthTotal == 0) {
        prevMonthTotal = element.open;
      }
      acumulatedRentability = (element.close / prevMonthTotal - 1) * 100;

      prevMonthTotal = element.close;
      ibovSeries.add(MoneyDateSeries(element.date, acumulatedRentability));
    }
        // }
        );
    return [
      new charts.Series<MoneyDateSeries, String>(
        id: "Rentabilidade",
        colorFn: (_, __) => charts.MaterialPalette.blue.shadeDefault,
        domainFn: (MoneyDateSeries history, _) =>
            DateFormat('MM-yy').format(history.date),
        areaColorFn: (_, __) =>
            charts.MaterialPalette.blue.shadeDefault.lighter,
        measureFn: (MoneyDateSeries history, _) => history.money,
        data: series,
      ),
      new charts.Series<MoneyDateSeries, String>(
        id: "IBOV",
        colorFn: (_, __) => charts.MaterialPalette.deepOrange.shadeDefault,
        domainFn: (MoneyDateSeries history, _) =>
            DateFormat('MM-yy').format(history.date),
        areaColorFn: (_, __) =>
            charts.MaterialPalette.deepOrange.shadeDefault.lighter,
        measureFn: (MoneyDateSeries history, _) => history.money,
        data: ibovSeries,
      ),
    ];
  }

  Future<List<charts.Series<MoneyDateSeries, DateTime>>>
      createTotalAmountSeries() async {
    PortfolioHistory portfolioHistory = await _futureHistory;
    List<MoneyDateSeries> seriesGross = [];
    List<MoneyDateSeries> seriesInvested = [];

    portfolioHistory.history.sort((a, b) => a.date.compareTo(b.date));

    double investedAmount = 0.0;
    portfolioHistory.history.forEach((element) {
      investedAmount += element.investedValue;
      seriesInvested.add(MoneyDateSeries(element.date, investedAmount));
      seriesGross.add(MoneyDateSeries(element.date, element.grossValue));
    });

    final now = DateTime.now();
    seriesGross.add(MoneyDateSeries(
        DateTime(now.year, now.month, 1), widget.summary.grossAmount));
    seriesInvested.add(MoneyDateSeries(
        DateTime(now.year, now.month, 1), widget.summary.investedAmount));

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
