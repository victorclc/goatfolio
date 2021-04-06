import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/common/chart/money_date_series.dart';
import 'package:goatfolio/common/chart/rentability_chart.dart';
import 'package:goatfolio/common/chart/valorization_chart.dart';
import 'package:goatfolio/common/formatter/brazil.dart';
import 'package:goatfolio/services/performance/model/portfolio_history.dart';
import 'package:goatfolio/services/performance/model/portfolio_performance.dart';
import 'package:charts_flutter/flutter.dart' as charts;
import 'package:intl/intl.dart';

void goToRentabilityPage(
    BuildContext context, PortfolioPerformance performance) async {
  await Navigator.push(
    context,
    CupertinoPageRoute(
      builder: (context) => RentabilityPage(performance),
    ),
  );
}

class RentabilityPage extends StatefulWidget {
  final PortfolioPerformance performance;

  const RentabilityPage(this.performance, {Key key}) : super(key: key);

  @override
  _RentabilityPageState createState() => _RentabilityPageState();
}

class _RentabilityPageState extends State<RentabilityPage> {
  final dateFormat = DateFormat('MMMM', 'pt_BR');
  String selectedTab;
  List<charts.Series<MoneyDateSeries, DateTime>> totalAmountSeries;
  MoneyDateSeries selectedGrossSeries;
  MoneyDateSeries selectedInvestedSeries;

  void initState() {
    super.initState();
    totalAmountSeries = createTotalAmountSeries();

    if (totalAmountSeries.first.data.isNotEmpty) {
      selectedGrossSeries = totalAmountSeries.first.data.last;
    }
    if (totalAmountSeries.last.data.isNotEmpty) {
      selectedInvestedSeries = totalAmountSeries.last.data.last;
    }
    selectedTab = 'a';
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;
    return CupertinoPageScaffold(
      navigationBar: CupertinoNavigationBar(
        backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
        previousPageTitle: "",
        middle: Text('Rentabilidade'),
      ),
      child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.only(left: 16, right: 16),
          child: Column(
            children: [
              Container(
                padding: EdgeInsets.only(top: 8, bottom: 4),
                width: double.infinity,
                child: CupertinoSlidingSegmentedControl(
                  groupValue: selectedTab ?? 'a',
                  children: {
                    'a': Text("Evolução",
                        style: textTheme.textStyle.copyWith(fontSize: 14)),
                    'b': Text("Rentabilidade",
                        style: textTheme.textStyle.copyWith(fontSize: 14))
                  },
                  onValueChanged: (value) {
                    setState(() {
                      selectedTab = value;
                    });
                  },
                ),
              ),
              totalAmountSeries.first.data.isEmpty
                  ? Center(
                      child: Text(
                      'Nenhum dado ainda.',
                      style: textTheme.textStyle,
                    ))
                  : selectedTab == 'a'
                      ? ValorizationChart(
                          totalAmountSeries: totalAmountSeries,
                        )
                      : RentabilityChart(
                          rentabilitySeries: createRentabilitySeries(),
                        ),
              // SizedBox(
              //   height: 240,
              //   child: totalAmountSeries.first.data.isNotEmpty
              //       ? LinearChart(
              //           createRentabilitySeries(),
              //           onSelectionChanged: onSelectionChanged,
              //         )
              //       : Center(
              //           child: Text(
              //           'Nenhum dado ainda.',
              //           style: textTheme.textStyle,
              //         )),
              // ),
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
                  Text(moneyFormatter.format(widget.performance.grossAmount),
                      style: textTheme.textStyle),
                ],
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('Valor investido', style: textTheme.textStyle),
                  Text(moneyFormatter.format(widget.performance.investedAmount),
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
                    moneyFormatter.format(widget.performance.result),
                    style: textTheme.textStyle.copyWith(
                        color: widget.performance.result >= 0
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

  List<charts.Series<MoneyDateSeries, DateTime>> createRentabilitySeries() {
    List<MoneyDateSeries> series = [];
    widget.performance.history.sort((a, b) => a.date.compareTo(b.date));
    double prevMonthTotal = 0.0;
    double acumulatedRentability = 0.0;

    for (PortfolioHistory element in widget.performance.history) {
      final monthTotal = element.grossAmount;
      acumulatedRentability +=
          ((monthTotal) / (prevMonthTotal + element.totalInvested) - 1) * 100;
      prevMonthTotal = monthTotal;
      series.add(MoneyDateSeries(element.date, acumulatedRentability));
      print(element.date.toIso8601String());
    }


    List<MoneyDateSeries> ibovSeries = [];
    widget.performance.ibovHistory.sort((a, b) => a.date.compareTo(b.date));
    prevMonthTotal = 0.0;
    acumulatedRentability = 0.0;
    widget.performance.ibovHistory.forEach((element) {
      // if (element.date.year < widget.performance.initialDate.year ||
      //     element.date.year == widget.performance.initialDate.year &&
      //         element.date.month < widget.performance.initialDate.month)
      //   print("data antiga");
      // else {
      //   print('data nova');
        if (prevMonthTotal == 0) {
          prevMonthTotal = element.openPrice;
        }
        acumulatedRentability +=
            (element.closePrice / prevMonthTotal - 1) * 100;
        print(acumulatedRentability);
        prevMonthTotal = element.closePrice;
        ibovSeries.add(MoneyDateSeries(element.date, acumulatedRentability));
      }
    // }
    );
    return [
      new charts.Series<MoneyDateSeries, DateTime>(
        id: "Rentabilidade",
        colorFn: (_, __) => charts.MaterialPalette.blue.shadeDefault,
        domainFn: (MoneyDateSeries history, _) => history.date,
        areaColorFn: (_, __) =>
            charts.MaterialPalette.blue.shadeDefault.lighter,
        measureFn: (MoneyDateSeries history, _) => history.money,
        data: series,
      ),
      new charts.Series<MoneyDateSeries, DateTime>(
        id: "IBOV",
        colorFn: (_, __) => charts.MaterialPalette.deepOrange.shadeDefault,
        domainFn: (MoneyDateSeries history, _) => history.date,
        areaColorFn: (_, __) =>
            charts.MaterialPalette.deepOrange.shadeDefault.lighter,
        measureFn: (MoneyDateSeries history, _) => history.money,
        data: ibovSeries,
      ),
    ];
  }

  List<charts.Series<MoneyDateSeries, DateTime>> createTotalAmountSeries() {
    List<MoneyDateSeries> seriesGross = [];
    List<MoneyDateSeries> seriesInvested = [];

    widget.performance.history.sort((a, b) => a.date.compareTo(b.date));
    widget.performance.history.forEach((element) {
      seriesGross.add(MoneyDateSeries(element.date, element.grossAmount));
    });

    double investedAmount = 0.0;
    widget.performance.history.forEach((history) {
      investedAmount += history.totalInvested;

      seriesInvested.add(MoneyDateSeries(history.date, investedAmount));
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
