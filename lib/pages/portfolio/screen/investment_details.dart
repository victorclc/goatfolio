import 'package:flutter/material.dart';
import 'package:flutter/cupertino.dart';
import 'package:goatfolio/common/chart/money_date_series.dart';
import 'package:goatfolio/common/chart/rentability_chart.dart';
import 'package:goatfolio/common/chart/valorization_chart.dart';
import 'package:goatfolio/common/formatter/brazil.dart';

import 'package:goatfolio/services/performance/model/stock_history.dart';
import 'package:goatfolio/services/performance/model/stock_performance.dart';
import 'package:intl/intl.dart';
import 'package:charts_flutter/flutter.dart' as charts;

void navigateToInvestmentDetails(BuildContext context, StockPerformance item,
    Color color, List<StockHistory> ibovHistory) {
  Navigator.of(context).push<void>(
    CupertinoPageRoute(
      builder: (context) => InvestmentDetails(
        title: "Detalhes",
        item: item,
        color: color,
        ibovHistory: ibovHistory,
      ),
    ),
  );
}

class InvestmentDetails extends StatefulWidget {
  final String title;
  final StockPerformance item;
  final Color color;
  final List<StockHistory> ibovHistory;

  const InvestmentDetails(
      {Key key, this.item, this.title, this.color, this.ibovHistory})
      : super(key: key);

  @override
  _InvestmentDetailsState createState() => _InvestmentDetailsState();
}

class _InvestmentDetailsState extends State<InvestmentDetails> {
  MoneyDateSeries selectedGrossSeries;
  MoneyDateSeries selectedInvestedSeries;
  List<charts.Series<MoneyDateSeries, DateTime>> totalAmountSeries;
  final dateFormat = DateFormat('MMMM', 'pt_BR');
  String selectedTab;

  void initState() {
    super.initState();
    totalAmountSeries = createTotalAmountSeries();
    selectedGrossSeries = totalAmountSeries.first.data.last;
    selectedInvestedSeries = totalAmountSeries.last.data.last;
    selectedTab = 'a';
  }

  void onSelectionChanged(Map<String, dynamic> series) {
    setState(() {
      selectedGrossSeries = series['Saldo bruto'];
      selectedInvestedSeries = series['Valor investido'];
    });
  }

  Widget _buildBody() {
    final textTheme = CupertinoTheme.of(context).textTheme;
    final currentValue = widget.item.currentAmount *
        (widget.item.currentStockPrice != null
            ? widget.item.currentStockPrice
            : 0.0);

    return SafeArea(
      child: SingleChildScrollView(
        child: Container(
          color: CupertinoTheme.of(context).scaffoldBackgroundColor,
          padding: EdgeInsets.all(16),
          child: Column(
            children: <Widget>[
              Container(
                alignment: Alignment.topLeft,
                child: Row(
                  children: <Widget>[
                    Container(
                      width: 4,
                      height: 14,
                      color: widget.color,
                    ),
                    Text(
                      " ${widget.item.ticker.replaceAll('.SA', '')}",
                      style: textTheme.textStyle.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
              SizedBox(
                height: 16,
              ),
              Container(
                width: double.infinity,
                child: CupertinoSlidingSegmentedControl(
                  groupValue: selectedTab ?? 'a',
                  children: {
                    'a': Text(
                      "Evolução",
                      style: textTheme.textStyle.copyWith(fontSize: 14),
                    ),
                    'b': Text(
                      "Rentabilidade",
                      style: textTheme.textStyle.copyWith(fontSize: 14),
                    ),
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
                      totalAmountSeries: totalAmountSeries,
                    )
                  : RentabilityChart(
                      rentabilitySeries: createRentabilitySeries(),
                    ),
              SizedBox(
                height: 16,
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
              _buildContentRow(
                  "Quantidade",
                  widget.item.currentAmount.toString(),
                  textTheme.textStyle,
                  textTheme.textStyle),
              _buildContentRow(
                  "Saldo bruto",
                  moneyFormatter.format(widget.item.currentAmount *
                      widget.item.currentStockPrice),
                  textTheme.textStyle,
                  textTheme.textStyle),
              _buildContentRow(
                  "Valor investido",
                  moneyFormatter.format(widget.item.currentInvested),
                  textTheme.textStyle,
                  textTheme.textStyle),
              SizedBox(
                height: 12,
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: <Widget>[
                  Text(
                    "Resultado",
                    style: textTheme.textStyle
                        .copyWith(fontSize: 16, fontWeight: FontWeight.w500),
                  ),
                  Text(
                    moneyFormatter
                        .format(currentValue - widget.item.currentInvested),
                    style: textTheme.textStyle.copyWith(
                        fontSize: 16,
                        color: currentValue - widget.item.currentInvested >= 0
                            ? Colors.green
                            : Colors.red),
                  ),
                ],
              ),
              SizedBox(
                height: 12,
              ),
              _buildContentRow(
                  "Cotação atual",
                  moneyFormatter.format(widget.item.currentStockPrice),
                  textTheme.textStyle,
                  textTheme.textStyle),
              _buildContentRow(
                  "Preço médio",
                  moneyFormatter.format(widget.item.averagePrice),
                  textTheme.textStyle,
                  textTheme.textStyle),
              SizedBox(
                height: 12,
              ),
              _buildContentRow(
                  "% preço médio",
                  percentFormatter.format((widget.item.currentStockPrice /
                          widget.item.averagePrice) -
                      1),
                  textTheme.textStyle,
                  textTheme.textStyle),
              Divider(
                height: 32,
                color: Colors.grey,
              ),
            ],
          ),
        ),
      ),
    );
  }

  List<charts.Series<MoneyDateSeries, DateTime>> createTotalAmountSeries() {
    List<MoneyDateSeries> seriesGross = [];
    List<MoneyDateSeries> seriesInvested = [];
    widget.item.history.sort((a, b) => a.date.compareTo(b.date));
    widget.item.history.forEach((element) {
      seriesGross.add(
          MoneyDateSeries(element.date, element.closePrice * element.amount));
    });

    double investedAmount = 0.0;
    widget.item.history.forEach((history) {
      if (history.amount == 0) {
        investedAmount = 0;
      } else {
        investedAmount += history.investedAmount;
      }
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

  List<charts.Series<MoneyDateSeries, DateTime>> createRentabilitySeries() {
    List<MoneyDateSeries> series = [];
    widget.item.history.sort((a, b) => a.date.compareTo(b.date));
    double prevMonthTotal = 0.0;
    double acumulatedRentability = 0.0;
    widget.item.history.forEach((element) {
      final monthTotal = element.amount * element.closePrice;
      acumulatedRentability +=
          ((monthTotal) / (prevMonthTotal + element.investedAmount) - 1) * 100;
      prevMonthTotal = monthTotal;
      series.add(MoneyDateSeries(element.date, acumulatedRentability));
    });

    List<MoneyDateSeries> ibovSeries = [];
    widget.ibovHistory.sort((a, b) => a.date.compareTo(b.date));
    prevMonthTotal = 0.0;
    acumulatedRentability = 0.0;
    print(widget.ibovHistory.length);
    widget.ibovHistory.forEach((element) {
      if (element.date.year < widget.item.initialDate.year ||
          element.date.year == widget.item.initialDate.year &&
              element.date.month < widget.item.initialDate.month)
        print("data antiga");
      else {
        print('data nova');
        if (prevMonthTotal == 0) {
          prevMonthTotal = element.openPrice;
        }
        acumulatedRentability +=
            (element.closePrice / prevMonthTotal - 1) * 100;
        print(acumulatedRentability);
        prevMonthTotal = element.closePrice;
        ibovSeries.add(MoneyDateSeries(element.date, acumulatedRentability));
      }
    });

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

  Widget _buildContentRow(String key, String value,
      [TextStyle keyStyle, TextStyle valueStyle]) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: <Widget>[
        Text(key, style: keyStyle),
        Text(
          value,
          style: valueStyle,
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return CupertinoPageScaffold(
      navigationBar: CupertinoNavigationBar(
        previousPageTitle: "",
        middle: Text(widget.title),
      ),
      child: _buildBody(),
    );
  }
}
