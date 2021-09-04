import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/common/formatter/brazil.dart';
import 'package:goatfolio/pages/portfolio/screen/investment_details.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/performance/model/benchmark_position.dart';
import 'package:goatfolio/services/performance/model/stock_summary.dart';
import 'package:provider/provider.dart';

class StockInvestmentSummaryItem extends StatelessWidget {
  final StockSummary summary;
  final Color color;
  final double portfolioTotalAmount;
  final double typeTotalAmount;
  final List<BenchmarkPosition> ibovHistory;

  const StockInvestmentSummaryItem(
      {Key key,
        @required this.summary,
        this.portfolioTotalAmount,
        @required this.color,
        this.typeTotalAmount,
        this.ibovHistory})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;
    final userService = Provider.of<UserService>(context, listen: false);
    final currentValue = summary.amount *
        (summary.currentPrice != null ? summary.currentPrice : 0.0);
    return CupertinoButton(
      padding: EdgeInsets.zero,
      onPressed: () {
        navigateToInvestmentDetails(
            context, summary, color, ibovHistory, userService);
      },
      child: Container(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            Container(
              padding: EdgeInsets.only(bottom: 8),
              child: Row(
                children: <Widget>[
                  Container(
                    width: 4,
                    height: 14,
                    color: color,
                  ),
                  Text(
                    " ${summary.currentTickerName.replaceAll('.SA', '')}",
                    style: textTheme.textStyle.copyWith(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: <Widget>[
                Row(
                  children: <Widget>[
                    Text(
                      "Saldo atual",
                      style: textTheme.textStyle.copyWith(fontSize: 16),
                    ),
                  ],
                ),
                Text(
                  moneyFormatter.format(currentValue),
                  style: textTheme.textStyle.copyWith(fontSize: 16),
                ),
              ],
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: <Widget>[
                Row(
                  children: <Widget>[
                    Text(
                      "Resultado",
                      style: textTheme.textStyle.copyWith(fontSize: 16),
                    ),
                  ],
                ),
                Text(
                  moneyFormatter.format(currentValue - summary.investedAmount),
                  style: textTheme.textStyle.copyWith(
                      fontSize: 16,
                      color: currentValue - summary.investedAmount < 0
                          ? Colors.red
                          : Colors.green),
                  // style: coloredStyle,
                ),
              ],
            ),
            SizedBox(
              height: 4,
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: <Widget>[
                Row(
                  children: <Widget>[
                    Text(
                      "% na categoria",
                      style: textTheme.textStyle.copyWith(fontSize: 16),
                    ),
                  ],
                ),
                Text(
                  percentFormatter.format(
                      (summary.currentPrice * summary.amount) /
                          typeTotalAmount),
                  style: textTheme.textStyle.copyWith(fontSize: 16),
                ),
              ],
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: <Widget>[
                Row(
                  children: <Widget>[
                    Text(
                      "% do portfolio",
                      style: textTheme.textStyle.copyWith(fontSize: 16),
                    ),
                  ],
                ),
                Text(
                  percentFormatter.format(
                      (summary.currentPrice * summary.amount) /
                          portfolioTotalAmount),
                  style: textTheme.textStyle.copyWith(fontSize: 16),
                ),
              ],
            ),
            Divider(
              height: 16,
              color: Colors.grey,
            ),
          ],
        ),
      ),
    );
  }
}