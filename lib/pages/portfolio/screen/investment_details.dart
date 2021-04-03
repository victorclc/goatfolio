import 'package:flutter/material.dart';
import 'package:flutter/cupertino.dart';
import 'package:goatfolio/common/formatter/brazil.dart';
import 'package:charts_flutter/flutter.dart' as charts;
import 'package:goatfolio/common/widget/linear_chart.dart';
import 'package:goatfolio/services/performance/model/stock_history.dart';
import 'package:goatfolio/services/performance/model/stock_performance.dart';
import 'package:intl/intl.dart';
import 'package:goatfolio/common/extension/string.dart';

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
  _MoneyDateSeries selectedGrossSeries;
  _MoneyDateSeries selectedInvestedSeries;
  List<charts.Series<_MoneyDateSeries, DateTime>> totalAmountSeries;
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
                  ? _ValorizationChart(
                      totalAmountSeries: totalAmountSeries,
                    )
                  : _RentabilityChart(
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

  List<charts.Series<_MoneyDateSeries, DateTime>> createTotalAmountSeries() {
    List<_MoneyDateSeries> seriesGross = [];
    List<_MoneyDateSeries> seriesInvested = [];
    widget.item.history.sort((a, b) => a.date.compareTo(b.date));
    widget.item.history.forEach((element) {
      seriesGross.add(
          _MoneyDateSeries(element.date, element.closePrice * element.amount));
    });

    double investedAmount = 0.0;
    widget.item.history.forEach((history) {
      if (history.amount == 0) {
        investedAmount = 0;
      } else {
        investedAmount += history.investedAmount;
      }
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

  List<charts.Series<_MoneyDateSeries, DateTime>> createRentabilitySeries() {
    List<_MoneyDateSeries> series = [];
    widget.item.history.sort((a, b) => a.date.compareTo(b.date));
    double prevMonthTotal = 0.0;
    double acumulatedRentability = 0.0;
    widget.item.history.forEach((element) {
      final monthTotal = element.amount * element.closePrice;
      acumulatedRentability +=
          ((monthTotal) / (prevMonthTotal + element.investedAmount) - 1) * 100;
      prevMonthTotal = monthTotal;
      series.add(_MoneyDateSeries(element.date, acumulatedRentability));
    });

    List<_MoneyDateSeries> ibovSeries = [];
    widget.ibovHistory.sort((a, b) => a.date.compareTo(b.date));
    prevMonthTotal = 0.0;
    acumulatedRentability = 0.0;
    print(widget.ibovHistory.length);
    widget.ibovHistory.forEach((element) {
      print(DateFormat('yyyy-MM-dd').format(element.date));
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
        ibovSeries.add(_MoneyDateSeries(element.date, acumulatedRentability));
      }
    });

    return [
      new charts.Series<_MoneyDateSeries, DateTime>(
        id: "Rentabilidade",
        colorFn: (_, __) => charts.MaterialPalette.blue.shadeDefault,
        domainFn: (_MoneyDateSeries history, _) => history.date,
        areaColorFn: (_, __) =>
            charts.MaterialPalette.blue.shadeDefault.lighter,
        measureFn: (_MoneyDateSeries history, _) => history.money,
        data: series,
      ),
      new charts.Series<_MoneyDateSeries, DateTime>(
        id: "IBOV",
        colorFn: (_, __) => charts.MaterialPalette.deepOrange.shadeDefault,
        domainFn: (_MoneyDateSeries history, _) => history.date,
        areaColorFn: (_, __) =>
            charts.MaterialPalette.deepOrange.shadeDefault.lighter,
        measureFn: (_MoneyDateSeries history, _) => history.money,
        data: ibovSeries,
      ),
    ];
  }

  // List<charts.Series<_MoneyDateSeries, DateTime>> createInvestedAmountSeries() {
  //   List<_MoneyDateSeries> series = [];
  //   widget.item.history.sort((a, b) => a.date.compareTo(b.date));
  //   double investedAmount = 0.0;
  //   widget.item.history.forEach((history) {
  //     investedAmount += history.investedAmount;
  //     series.add(_MoneyDateSeries(history.date, investedAmount));
  //   });
  //   return [
  //     new charts.Series<_MoneyDateSeries, DateTime>(
  //       id: "invested",
  //       colorFn: (_, __) => charts.MaterialPalette.blue.shadeDefault,
  //       domainFn: (_MoneyDateSeries history, _) => history.date,
  //       measureFn: (_MoneyDateSeries history, _) => history.money,
  //       data: series,
  //     ),
  //   ];
  // }

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

class _MoneyDateSeries {
  final DateTime date;
  final double money;

  _MoneyDateSeries(this.date, this.money);
}

class _ValorizationChart extends StatefulWidget {
  final List<charts.Series> totalAmountSeries;

  const _ValorizationChart({Key key, this.totalAmountSeries}) : super(key: key);

  @override
  _ValorizationChartState createState() => _ValorizationChartState();
}

class _ValorizationChartState extends State<_ValorizationChart> {
  _MoneyDateSeries selectedGrossSeries;
  _MoneyDateSeries selectedInvestedSeries;
  final dateFormat = DateFormat('MMMM', 'pt_BR');

  @override
  void initState() {
    super.initState();
    selectedGrossSeries = widget.totalAmountSeries.first.data.last;
    selectedInvestedSeries = widget.totalAmountSeries.last.data.last;
  }

  void onSelectionChanged(Map<String, dynamic> series) {
    setState(() {
      selectedGrossSeries = series['Saldo bruto'];
      selectedInvestedSeries = series['Valor investido'];
    });
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;
    return Column(
      children: [
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
            widget.totalAmountSeries,
            onSelectionChanged: onSelectionChanged,
          ),
        ),
      ],
    );
  }
}

class _RentabilityChart extends StatefulWidget {
  final List<charts.Series> rentabilitySeries;

  const _RentabilityChart({Key key, this.rentabilitySeries}) : super(key: key);

  @override
  _RentabilityChartState createState() => _RentabilityChartState();
}

class _RentabilityChartState extends State<_RentabilityChart> {
  _MoneyDateSeries selectedGrossSeries;
  _MoneyDateSeries selectedIbovSeries;
  final dateFormat = DateFormat('MMMM', 'pt_BR');

  @override
  void initState() {
    super.initState();
    selectedGrossSeries = widget.rentabilitySeries.first.data.last;
    selectedIbovSeries = widget.rentabilitySeries.last.data.last;
  }

  void onSelectionChanged(Map<String, dynamic> series) {
    setState(() {
      selectedGrossSeries = series['Rentabilidade'];
      selectedIbovSeries = series['IBOV'];
    });
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;
    return Column(
      children: [
        Container(
          padding: EdgeInsets.only(top: 4),
          alignment: Alignment.centerLeft,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Rentabilidade',
                style: textTheme.tabLabelTextStyle.copyWith(fontSize: 16),
              ),
              Text(
                percentFormatter.format(selectedGrossSeries.money / 100),
                style: textTheme.textStyle
                    .copyWith(fontSize: 28, fontWeight: FontWeight.w500),
              ),
              Text(
                'Ibovespa',
                style: textTheme.tabLabelTextStyle.copyWith(fontSize: 16),
              ),
              Text(
                percentFormatter.format(selectedIbovSeries.money / 100),
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
            widget.rentabilitySeries,
            onSelectionChanged: onSelectionChanged,
          ),
        ),
      ],
    );
  }
}
