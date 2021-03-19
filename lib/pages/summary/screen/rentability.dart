import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/common/formatter/brazil.dart';
import 'package:goatfolio/common/widget/linear_chart.dart';
import 'package:goatfolio/services/performance/model/portfolio_performance.dart';
import 'package:charts_flutter/flutter.dart' as charts;
import 'package:goatfolio/common/extension/string.dart';
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
  List<charts.Series<_MoneyDateSeries, DateTime>> totalAmountSeries;
  _MoneyDateSeries selectedGrossSeries;
  _MoneyDateSeries selectedInvestedSeries;

  void initState() {
    super.initState();
    totalAmountSeries = createTotalAmountSeries();

    selectedGrossSeries = totalAmountSeries.first.data.last;
    selectedInvestedSeries = totalAmountSeries.last.data.last;
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
                    'a': Text("Valorização"),
                    'b': Text("Rentabilidade")
                  },
                  onValueChanged: (value) {
                    setState(() {
                      selectedTab = value;
                    });
                  },
                ),
              ),
              Container(
                padding: EdgeInsets.only(top: 4),
                alignment: Alignment.centerLeft,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Saldo bruto',
                      style: textTheme.tabLabelTextStyle.copyWith(fontSize: 16),
                    ),
                    Text(
                      moneyFormatter.format(selectedGrossSeries.money),
                      style: textTheme.textStyle
                          .copyWith(fontSize: 28, fontWeight: FontWeight.w500),
                    ),
                    Text(
                      'Valor investido',
                      style: textTheme.tabLabelTextStyle.copyWith(fontSize: 16),
                    ),
                    Text(
                      moneyFormatter.format(selectedInvestedSeries.money),
                      style: textTheme.textStyle
                          .copyWith(fontSize: 20, fontWeight: FontWeight.w500),
                    ),
                    Text(
                      '${dateFormat.format(selectedGrossSeries.date).capitalize()} de ${selectedGrossSeries.date.year}',
                      style: textTheme.tabLabelTextStyle
                          .copyWith(fontSize: 16, fontWeight: FontWeight.w400),
                    ),
                  ],
                ),
              ),
              SizedBox(
                height: 240,
                child: LinearChart(
                  totalAmountSeries,
                  onSelectionChanged: onSelectionChanged,
                ),
              ),
              Divider(
                color: Colors.grey,
                height: 24,
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('Saldo bruto'),
                  Text(moneyFormatter.format(widget.performance.grossAmount)),
                ],
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('Valor investido'),
                  Text(
                      moneyFormatter.format(widget.performance.investedAmount)),
                ],
              ),
              SizedBox(
                height: 4,
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('Resultado'),
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

  List<charts.Series<_MoneyDateSeries, DateTime>> createTotalAmountSeries() {
    List<_MoneyDateSeries> seriesGross = [];
    List<_MoneyDateSeries> seriesInvested = [];

    widget.performance.history.sort((a, b) => a.date.compareTo(b.date));
    widget.performance.history.forEach((element) {
      seriesGross.add(_MoneyDateSeries(element.date, element.grossAmount));
    });

    double investedAmount = 0.0;
    widget.performance.history.forEach((history) {
      investedAmount += history.totalInvested;

      seriesInvested.add(_MoneyDateSeries(history.date, investedAmount));
    });

    return [
      new charts.Series<_MoneyDateSeries, DateTime>(
        id: "Saldo bruto",
        colorFn: (_, __) => charts.MaterialPalette.blue.shadeDefault,
        domainFn: (_MoneyDateSeries history, _) => history.date,
        areaColorFn: (_, __) =>
            charts.MaterialPalette.blue.shadeDefault.lighter,
        measureFn: (_MoneyDateSeries history, _) => history.money,
        data: seriesGross,
      ),
      new charts.Series<_MoneyDateSeries, DateTime>(
        id: "Valor investido",
        colorFn: (_, __) => charts.MaterialPalette.deepOrange.shadeDefault,
        domainFn: (_MoneyDateSeries history, _) => history.date,
        dashPatternFn: (_, __) => [2, 2],
        measureFn: (_MoneyDateSeries history, _) => history.money,
        data: seriesInvested,
      ),
    ];
  }

  void onSelectionChanged(Map<String, dynamic> series) {
    setState(() {
      selectedGrossSeries = series['Saldo bruto'];
      selectedInvestedSeries = series['Valor investido'];
    });
  }
}

class _MoneyDateSeries {
  final DateTime date;
  final double money;

  _MoneyDateSeries(this.date, this.money);
}
