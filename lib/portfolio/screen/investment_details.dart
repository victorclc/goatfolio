import 'package:flutter/material.dart';
import 'package:flutter/cupertino.dart';
import 'package:goatfolio/common/formatter/brazil.dart';
import 'package:charts_flutter/flutter.dart' as charts;
import 'package:goatfolio/performance/model/stock_history.dart';
import 'package:goatfolio/performance/model/stock_performance.dart';
import 'package:goatfolio/portfolio/widget/linear_chart.dart';

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
  var _dataSeries;

  void initState() {
    super.initState();
  }

  Widget _buildBody() {
    final currentValue = widget.item.currentAmount *
        (widget.item.currentStockPrice != null ? widget.item.currentStockPrice : 0.0);
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
                      currentValue - widget.item.currentInvested),
                  style: TextStyle(
                      fontSize: 16,
                      color: currentValue -
                                  widget.item.currentInvested >=
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
                "Quantidade", widget.item.currentAmount.toString()),
            _buildContentRow(
                "Saldo bruto",
                moneyFormatter
                    .format(widget.item.currentAmount * widget.item.currentStockPrice)),
            _buildContentRow("Valor investido",
                moneyFormatter.format(widget.item.currentInvested)),
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
            _buildContentRow(
                "Rentabilidade",
                percentFormatter.format(
                    100 / 100)),
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

  List<charts.Series<StockHistory, DateTime>>
      createTotalAmountSeries() {
    return [
      new charts.Series<StockHistory, DateTime>(
        id: "valor",
        colorFn: (_, __) => charts.MaterialPalette.blue.shadeDefault,
        domainFn: (StockHistory history, _) => history.date,
        measureFn: (StockHistory history, _) => history.amount * history.closePrice,
        data: widget.item.history..sort((a,b) => a.date.compareTo(b.date)),
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
