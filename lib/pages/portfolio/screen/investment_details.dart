import 'package:flutter/material.dart';
import 'package:flutter/cupertino.dart';
import 'package:goatfolio/common/formatter/brazil.dart';
import 'package:charts_flutter/flutter.dart' as charts;
import 'package:goatfolio/pages/portfolio/widget/linear_chart.dart';
import 'package:goatfolio/services/performance/model/stock_performance.dart';
import 'package:intl/intl.dart';
import 'package:goatfolio/common/extension/string.dart';

void navigateToInvestmentDetails(
    BuildContext context, StockPerformance item, Color color) {
  Navigator.of(context).push<void>(
    CupertinoPageRoute(
      builder: (context) => InvestmentDetails(
        title: "Detalhes",
        item: item,
        color: color,
      ),
    ),
  );
}

class InvestmentDetails extends StatefulWidget {
  final String title;
  final StockPerformance item;
  final Color color;

  const InvestmentDetails({Key key, this.item, this.title, this.color})
      : super(key: key);

  @override
  _InvestmentDetailsState createState() => _InvestmentDetailsState();
}

class _InvestmentDetailsState extends State<InvestmentDetails> {
  _MoneyDateSeries selectedSeries;
  List<charts.Series<_MoneyDateSeries, DateTime>> totalAmountSeries;
  final dateFormat = DateFormat('MMMM', 'pt_BR');
  String selectedTab;

  void initState() {
    super.initState();
    totalAmountSeries = createTotalAmountSeries();
    selectedSeries = totalAmountSeries.first.data.last;
  }

  void onSelectionChanged(_MoneyDateSeries series) {
    setState(() {
      selectedSeries = series;
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
                      style: TextStyle(
                        fontSize: 16,
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
                    'a': Text("Valorização"),
                    'b': Text("Rentabilidade")
                  },
                  onValueChanged: (value){
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
                      moneyFormatter.format(selectedSeries.money),
                      style: textTheme.textStyle
                          .copyWith(fontSize: 28, fontWeight: FontWeight.w500),
                    ),
                    Text(
                      '${dateFormat.format(selectedSeries.date).capitalize()} de ${selectedSeries.date.year}',
                      style: textTheme.tabLabelTextStyle
                          .copyWith(fontSize: 16, fontWeight: FontWeight.w400),
                    ),
                  ],
                ),
              ),
              SizedBox(
                height: 240,
                child: LinearChartChart(
                  createTotalAmountSeries(),
                  onSelectionChanged: onSelectionChanged,
                ),
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
                  "Quantidade", widget.item.currentAmount.toString()),
              _buildContentRow(
                  "Saldo bruto",
                  moneyFormatter.format(widget.item.currentAmount *
                      widget.item.currentStockPrice)),
              _buildContentRow("Valor investido",
                  moneyFormatter.format(widget.item.currentInvested)),
              SizedBox(
                height: 12,
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: <Widget>[
                  Text(
                    "Resultado",
                    style: TextStyle(fontWeight: FontWeight.w600),
                  ),
                  Text(
                    moneyFormatter
                        .format(currentValue - widget.item.currentInvested),
                    style: TextStyle(
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
              _buildContentRow("Cotação atual",
                  moneyFormatter.format(widget.item.currentStockPrice)),
              _buildContentRow("Preço médio",
                  moneyFormatter.format(widget.item.averagePrice)),
              SizedBox(
                height: 12,
              ),
              _buildContentRow(
                  "% preço médio",
                  percentFormatter.format((widget.item.currentStockPrice /
                          widget.item.averagePrice) -
                      1)),
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

    return [
      new charts.Series<_MoneyDateSeries, DateTime>(
        id: "gross",
        colorFn: (_, __) => charts.MaterialPalette.blue.shadeDefault,
        domainFn: (_MoneyDateSeries history, _) => history.date,
        areaColorFn: (_, __) =>
            charts.MaterialPalette.blue.shadeDefault.lighter,
        measureFn: (_MoneyDateSeries history, _) => history.money,
        data: seriesGross,
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

  Widget _buildContentRow(String key, String value, [TextStyle style]) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: <Widget>[
        Text(key),
        Text(
          value,
          style: style,
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
