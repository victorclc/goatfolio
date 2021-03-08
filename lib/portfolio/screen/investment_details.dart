import 'package:flutter/material.dart';
import 'package:flutter/cupertino.dart';
import 'package:goatfolio/common/formatter/brazil.dart';
import 'package:charts_flutter/flutter.dart' as charts;
import 'package:goatfolio/performance/model/monthly_performance.dart';
import 'package:goatfolio/performance/model/performance_history.dart';
import 'package:goatfolio/portfolio/widget/linear_chart.dart';
import 'package:intl/intl.dart';

void navigateToInvestmentDetails(
    BuildContext context, StockMonthlyPerformance item, Color color) {
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
  final StockMonthlyPerformance item;
  final Color color;

  const InvestmentDetails({Key key, this.item, this.title, this.color})
      : super(key: key);

  @override
  _InvestmentDetailsState createState() => _InvestmentDetailsState();
}

class _InvestmentDetailsState extends State<InvestmentDetails> {
  var _dataSeries;

  void initState() {
    super.initState();
  }

  Widget _buildBody() {
    return SafeArea(
      child: Container(
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
            Divider(
              height: 24,
              color: Colors.grey,
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: <Widget>[
                Text(
                  "Resultado",
                  style: TextStyle(fontWeight: FontWeight.w600),
                ),
                Text(
                  moneyFormatter.format(
                      widget.item.performanceHistory.last.monthTotal -
                          widget.item.position.currentInvested),
                  style: TextStyle(
                      fontSize: 16,
                      color: widget.item.performanceHistory.last.monthTotal -
                                  widget.item.position.currentInvested >=
                              0
                          ? Colors.green
                          : Colors.red),
                ),
              ],
            ),
            SizedBox(
              height: 16,
            ),
            _buildContentRow(
                "Quantidade", widget.item.position.currentAmount.toString()),
            _buildContentRow(
                "Saldo bruto",
                moneyFormatter
                    .format(widget.item.performanceHistory.last.monthTotal)),
            _buildContentRow("Valor investido",
                moneyFormatter.format(widget.item.position.currentInvested)),
            SizedBox(
              height: 12,
            ),
            _buildContentRow("Cotação atual",
                moneyFormatter.format(widget.item.currentPrice)),
            _buildContentRow("Preço médio",
                moneyFormatter.format(widget.item.position.averagePrice)),
            SizedBox(
              height: 12,
            ),
            _buildContentRow(
                "% preço médio",
                percentFormatter.format((widget.item.currentPrice /
                        widget.item.position.averagePrice) -
                    1)),
            _buildContentRow(
                "Rentabilidade",
                percentFormatter.format(
                    widget.item.performanceHistory.last.rentability / 100)),
            Divider(
              height: 32,
              color: Colors.grey,
            ),
            SizedBox(
              height: 240,
              child: LinearChart(
                createTotalAmountSeries(),
              ),
            ),
          ],
        ),
      ),
    );
  }

  List<charts.Series<StockPerformanceHistory, DateTime>>
      createTotalAmountSeries() {
    return [
      new charts.Series<StockPerformanceHistory, DateTime>(
        id: "valor",
        colorFn: (_, __) => charts.MaterialPalette.blue.shadeDefault,
        domainFn: (StockPerformanceHistory history, _) => history.date,
        measureFn: (StockPerformanceHistory history, _) => history.monthTotal,
        data: widget.item.performanceHistory,
      ),
    ];
  }

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
