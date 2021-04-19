import 'package:flutter/material.dart';
import 'package:flutter/cupertino.dart';
import 'package:goatfolio/common/chart/money_date_series.dart';
import 'package:goatfolio/common/chart/rentability_chart.dart';
import 'package:goatfolio/common/chart/valorization_chart.dart';
import 'package:goatfolio/common/formatter/brazil.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/performance/client/performance_client.dart';

import 'package:goatfolio/services/performance/model/stock_position.dart';
import 'package:goatfolio/services/performance/model/stock_summary.dart';
import 'package:goatfolio/services/performance/model/ticker_consolidated_history.dart';
import 'package:intl/intl.dart';
import 'package:charts_flutter/flutter.dart' as charts;
import 'package:provider/provider.dart';

void navigateToInvestmentDetails(BuildContext context, StockSummary item,
    Color color, List<StockPosition> ibovHistory) {
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
  final StockSummary item;
  final Color color;
  final List<StockPosition> ibovHistory;

  const InvestmentDetails(
      {Key key, this.item, this.title, this.color, this.ibovHistory})
      : super(key: key);

  @override
  _InvestmentDetailsState createState() => _InvestmentDetailsState();
}

class _InvestmentDetailsState extends State<InvestmentDetails> {
  final dateFormat = DateFormat('MMMM', 'pt_BR');
  MoneyDateSeries selectedGrossSeries;
  MoneyDateSeries selectedInvestedSeries;
  String selectedTab;
  PerformanceClient _client;
  Future<TickerConsolidatedHistory> _futureHistory;

  void initState() {
    super.initState();
    final userService = Provider.of<UserService>(context, listen: false);
    _client = PerformanceClient(userService);
    _futureHistory = _client.getTickerConsolidatedHistory(widget.item.ticker);
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
    final currentValue = widget.item.amount *
        (widget.item.currentPrice != null ? widget.item.currentPrice : 0.0);

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
                      " ${widget.item.currentTickerName.replaceAll('.SA', '')}",
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
                      totalAmountSeries: createTotalAmountSeries(),
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
              _buildContentRow("Quantidade", widget.item.amount.toString(),
                  textTheme.textStyle, textTheme.textStyle),
              _buildContentRow(
                  "Saldo bruto",
                  moneyFormatter
                      .format(widget.item.amount * widget.item.currentPrice),
                  textTheme.textStyle,
                  textTheme.textStyle),
              _buildContentRow(
                  "Valor investido",
                  moneyFormatter.format(widget.item.investedAmount),
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
                        .format(currentValue - widget.item.investedAmount),
                    style: textTheme.textStyle.copyWith(
                        fontSize: 16,
                        color: currentValue - widget.item.investedAmount >= 0
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
                  moneyFormatter.format(widget.item.currentPrice),
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
                  percentFormatter.format(
                      (widget.item.currentPrice / widget.item.averagePrice) -
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

  Future<List<charts.Series<MoneyDateSeries, DateTime>>>
      createTotalAmountSeries() async {
    TickerConsolidatedHistory tickerHistory = await _futureHistory;
    List<MoneyDateSeries> seriesGross = [];
    List<MoneyDateSeries> seriesInvested = [];

    tickerHistory.history.sort((a, b) => a.date.compareTo(b.date));
    double investedAmount = 0.0;
    tickerHistory.history.forEach((element) {
      if (element.amount == 0) {
        investedAmount = 0;
      } else {
        investedAmount += element.investedValue - element.soldValue;
      }
      seriesInvested.add(MoneyDateSeries(element.date, investedAmount));
      seriesGross.add(
          MoneyDateSeries(element.date, element.closePrice * element.amount));
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

  Future<List<charts.Series<MoneyDateSeries, DateTime>>> createRentabilitySeries() async{
    // List<MoneyDateSeries> series = [];
    // widget.item.history.sort((a, b) => a.date.compareTo(b.date));
    // double prevMonthTotal = 0.0;
    // double acumulatedRentability = 0.0;
    // widget.item.history.forEach((element) {
    //   final monthTotal = element.amount * element.closePrice;
    //   acumulatedRentability +=
    //       ((monthTotal) / (prevMonthTotal + element.investedAmount) - 1) * 100;
    //   prevMonthTotal = monthTotal;
    //   series.add(MoneyDateSeries(element.date, acumulatedRentability));
    // });
    //
    // List<MoneyDateSeries> ibovSeries = [];
    // widget.ibovHistory.sort((a, b) => a.date.compareTo(b.date));
    // prevMonthTotal = 0.0;
    // acumulatedRentability = 0.0;
    // print(widget.ibovHistory.length);
    // widget.ibovHistory.forEach((element) {
    //   if (element.date.year < widget.item.initialDate.year ||
    //       element.date.year == widget.item.initialDate.year &&
    //           element.date.month < widget.item.initialDate.month)
    //     print("data antiga");
    //   else {
    //     print('data nova');
    //     if (prevMonthTotal == 0) {
    //       prevMonthTotal = element.openPrice;
    //     }
    //     acumulatedRentability +=
    //         (element.closePrice / prevMonthTotal - 1) * 100;
    //     print(acumulatedRentability);
    //     prevMonthTotal = element.closePrice;
    //     ibovSeries.add(MoneyDateSeries(element.date, acumulatedRentability));
    //   }
    // });
    //
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
