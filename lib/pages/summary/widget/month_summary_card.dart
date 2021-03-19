import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/common/formatter/brazil.dart';
import 'package:goatfolio/common/widget/pressable_card.dart';
import 'package:goatfolio/services/performance/model/portfolio_performance.dart';

class MonthSummaryCard extends StatefulWidget {
  static const String CARD_TITLE = "Rentabilidade";
  final PortfolioPerformance performance;

  const MonthSummaryCard(this.performance, {Key key}) : super(key: key);

  @override
  _MonthSummaryCardState createState() {
    return _MonthSummaryCardState();
  }
}

class _MonthSummaryCardState extends State<MonthSummaryCard> {
  var sortedHistory;

  void initState() {
    super.initState();
    sortedHistory = widget.performance.history
      ..sort((a, b) => a.date.compareTo(b.date));
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;
    return Container(
      width: double.infinity,
      child: PressableCard(
        onPressed: () => {},
        child: Column(
          children: [
            Container(
              alignment: Alignment.centerLeft,
              padding: EdgeInsets.only(left: 16, right: 16, top: 16, bottom: 8),
              child: Text(
                'Rentabilidade',
                style: CupertinoTheme.of(context).textTheme.navTitleTextStyle,
              ),
            ),
            Padding(
              padding: const EdgeInsets.only(bottom: 16.0, left: 16, right: 16),
              child: Column(
                children: [
                  Align(
                      alignment: Alignment.centerLeft,
                      child: Text('Saldo bruto',
                          style: textTheme.tabLabelTextStyle
                              .copyWith(fontSize: 16))),
                  Align(
                    alignment: Alignment.centerLeft,
                    child: Text(
                      moneyFormatter.format(widget.performance.grossAmount),
                      style: textTheme.textStyle
                          .copyWith(fontSize: 24, fontWeight: FontWeight.w500),
                    ),
                  ),
                  SizedBox(
                    height: 8,
                  ),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            'Variação no mês: ',
                            style: textTheme.textStyle
                                .copyWith(fontSize: 16),
                          ),
                          Text(
                            moneyFormatter.format(
                                widget.performance.grossAmount -
                                    widget
                                        .performance
                                        .history[widget.performance
                                                .history.length -
                                            2]
                                        .grossAmount),
                            style: Theme.of(context)
                                .textTheme
                                .bodyText2
                                .copyWith(
                                    color: widget.performance
                                                    .grossAmount -
                                                widget
                                                    .performance
                                                    .history[widget
                                                            .performance
                                                            .history
                                                            .length -
                                                        2]
                                                    .grossAmount >=
                                            0
                                        ? Colors.green
                                        : Colors.red,
                                    fontSize: 16),
                          ),
                        ],
                      ),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            'Variação no dia: ',
                            style: textTheme.textStyle
                                .copyWith(fontSize: 16),
                          ),
                          Text(
                            moneyFormatter
                                .format(widget.performance.dayVariation),
                            style: Theme.of(context)
                                .textTheme
                                .bodyText2
                                .copyWith(
                                    color:
                                        widget.performance.dayVariation >=
                                                0
                                            ? Colors.green
                                            : Colors.red,
                                    fontSize: 16),
                          ),
                        ],
                      ),
                    ],
                  ),
                  // Row(
                  //   mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  //   children: [
                  //     Text('Variação no dia'),
                  //     Text(
                  //       moneyFormatter.format(widget.performance.dayVariation),
                  //       style: Theme.of(context).textTheme.bodyText2.copyWith(
                  //           color: widget.performance.dayVariation >= 0
                  //               ? Colors.green
                  //               : Colors.red,
                  //           fontSize: 16),
                  //     ),
                  //   ],
                  // ),

                  SizedBox(
                    height: 8,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
