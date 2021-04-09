import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/common/chart/money_date_series.dart';
import 'package:goatfolio/common/chart/rentability_chart.dart';
import 'package:goatfolio/common/chart/valorization_chart.dart';
import 'package:goatfolio/common/formatter/brazil.dart';
import 'package:goatfolio/services/performance/model/portfolio_history.dart';
import 'package:charts_flutter/flutter.dart' as charts;
import 'package:goatfolio/services/performance/model/portfolio_summary.dart';
import 'package:intl/intl.dart';

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
  String selectedTab;
  MoneyDateSeries selectedGrossSeries;
  MoneyDateSeries selectedInvestedSeries;

  void initState() {
    super.initState();
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
              selectedTab == 'a'
                      ? ValorizationChart(
                          totalAmountSeries: createTotalAmountSeries(),
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

  List<charts.Series<MoneyDateSeries, DateTime>> createRentabilitySeries() {
    // List<MoneyDateSeries> series = [];
    // widget.summary.history.sort((a, b) => a.date.compareTo(b.date));
    // double prevMonthTotal = 0.0;
    // double acumulatedRentability = 0.0;
    //
    // for (PortfolioHistory element in widget.summary.history) {
    //   final monthTotal = element.grossAmount;
    //   acumulatedRentability +=
    //       ((monthTotal) / (prevMonthTotal + element.totalInvested) - 1) * 100;
    //   prevMonthTotal = monthTotal;
    //   series.add(MoneyDateSeries(element.date, acumulatedRentability));
    // }
    // print("FINAL");
    // print((widget.summary.grossAmount / prevMonthTotal - 1) * 100);
    // print(acumulatedRentability);
    // final now = DateTime.now();
    // acumulatedRentability +=
    //     (widget.summary.grossAmount / prevMonthTotal - 1) * 100;
    // print(acumulatedRentability);
    // series.add(MoneyDateSeries(
    //     DateTime(now.year, now.month, 1), acumulatedRentability));
    //
    // List<MoneyDateSeries> ibovSeries = [];
    // widget.summary.ibovHistory.sort((a, b) => a.date.compareTo(b.date));
    // prevMonthTotal = 0.0;
    // acumulatedRentability = 0.0;
    // widget.summary.ibovHistory.forEach((element) {
    //   // if (element.date.year < widget.performance.initialDate.year ||
    //   //     element.date.year == widget.performance.initialDate.year &&
    //   //         element.date.month < widget.performance.initialDate.month)
    //   //   print("data antiga");
    //   // else {
    //   //   print('data nova');
    //   if (prevMonthTotal == 0) {
    //     prevMonthTotal = element.openPrice;
    //   }
    //   acumulatedRentability += (element.closePrice / prevMonthTotal - 1) * 100;
    //   print(acumulatedRentability);
    //   prevMonthTotal = element.closePrice;
    //   ibovSeries.add(MoneyDateSeries(element.date, acumulatedRentability));
    // }
    //     // }
    //     );
    // return [
    //   new charts.Series<MoneyDateSeries, DateTime>(
    //     id: "Rentabilidade",
    //     colorFn: (_, __) => charts.MaterialPalette.blue.shadeDefault,
    //     domainFn: (MoneyDateSeries history, _) => history.date,
    //     areaColorFn: (_, __) =>
    //         charts.MaterialPalette.blue.shadeDefault.lighter,
    //     measureFn: (MoneyDateSeries history, _) => history.money,
    //     data: series,
    //   ),
    //   new charts.Series<MoneyDateSeries, DateTime>(
    //     id: "IBOV",
    //     colorFn: (_, __) => charts.MaterialPalette.deepOrange.shadeDefault,
    //     domainFn: (MoneyDateSeries history, _) => history.date,
    //     areaColorFn: (_, __) =>
    //         charts.MaterialPalette.deepOrange.shadeDefault.lighter,
    //     measureFn: (MoneyDateSeries history, _) => history.money,
    //     data: ibovSeries,
    //   ),
    // ];
    return null;
  }

  List<charts.Series<MoneyDateSeries, DateTime>> createTotalAmountSeries() {
    // List<MoneyDateSeries> seriesGross = [];
    // List<MoneyDateSeries> seriesInvested = [];
    //
    // widget.summary.history.sort((a, b) => a.date.compareTo(b.date));
    // widget.summary.history.forEach((element) {
    //   seriesGross.add(MoneyDateSeries(element.date, element.grossAmount));
    // });
    // final now = DateTime.now();
    // seriesGross.add(MoneyDateSeries(
    //     DateTime(now.year, now.month, 1), widget.summary.grossAmount));
    //
    // double investedAmount = 0.0;
    // widget.summary.history.forEach((history) {
    //   investedAmount += history.totalInvested;
    //
    //   seriesInvested.add(MoneyDateSeries(history.date, investedAmount));
    // });
    // seriesInvested.add(MoneyDateSeries(
    //     DateTime(now.year, now.month, 1), widget.summary.investedAmount));
    //
    // return [
    //   new charts.Series<MoneyDateSeries, DateTime>(
    //     id: "Saldo bruto",
    //     colorFn: (_, __) => charts.MaterialPalette.blue.shadeDefault,
    //     domainFn: (MoneyDateSeries history, _) => history.date,
    //     areaColorFn: (_, __) =>
    //         charts.MaterialPalette.blue.shadeDefault.lighter,
    //     measureFn: (MoneyDateSeries history, _) => history.money,
    //     data: seriesGross,
    //   ),
    //   new charts.Series<MoneyDateSeries, DateTime>(
    //     id: "Valor investido",
    //     colorFn: (_, __) => charts.MaterialPalette.deepOrange.shadeDefault,
    //     domainFn: (MoneyDateSeries history, _) => history.date,
    //     dashPatternFn: (_, __) => [2, 2],
    //     measureFn: (MoneyDateSeries history, _) => history.money,
    //     data: seriesInvested,
    //   ),
    // ];
    return null;
  }
}
