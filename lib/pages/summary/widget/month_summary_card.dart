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
  @override
  void initState() {
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      child: PressableCard(
        onPressed: () => {},
        child: Column(
          children: [
            Container(
              alignment: Alignment.centerLeft,
              padding: EdgeInsets.all(16),
              child: Text(
                'Rentabilidade',
                style: Theme.of(context).textTheme.bodyText2.copyWith(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.only(bottom: 16.0, left: 16, right: 16),
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Total bruto'),
                      Text(
                        moneyFormatter.format(widget.performance.grossAmount),
                        style: Theme.of(context)
                            .textTheme
                            .bodyText2
                            .copyWith(fontSize: 16),
                      ),
                    ],
                  ),
                  SizedBox(
                    height: 4,
                  ),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Variação no dia'),
                      Text(
                        moneyFormatter.format(widget.performance.dayVariation),
                        style: Theme.of(context).textTheme.bodyText2.copyWith(
                            color: widget.performance.dayVariation >= 0
                                ? Colors.green
                                : Colors.red,
                            fontSize: 16),
                      ),
                    ],
                  ),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Variação no mês'),
                      Text(
                        moneyFormatter.format(widget.performance.grossAmount -
                            widget
                                .performance
                                .history[widget.performance.history.length - 2]
                                .grossAmount),
                        style: Theme.of(context).textTheme.bodyText2.copyWith(
                            color: widget.performance.grossAmount -
                                        widget
                                            .performance
                                            .history[widget.performance.history
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
                  SizedBox(
                    height: 8,
                  ),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Row(
                        children: [
                          Row(
                            children: [
                              Text("Carteira: "),
                              Text(
                                percentFormatter.format(widget
                                        .performance
                                        .history[
                                            widget.performance.history.length -
                                                2]
                                        .grossAmount /
                                    widget.performance.grossAmount),
                                style: Theme.of(context)
                                    .textTheme
                                    .bodyText2
                                    .copyWith(color: Colors.lightBlue),
                              ),
                            ],
                          ),
                        ],
                      ),
                      Row(
                        children: [
                          Text("CDI: "),
                          Text(
                            percentFormatter.format(widget
                                    .performance
                                    .history[
                                        widget.performance.history.length - 2]
                                    .grossAmount /
                                widget.performance.grossAmount),
                            style: Theme.of(context)
                                .textTheme
                                .bodyText2
                                .copyWith(color: Colors.deepPurple),
                          )
                        ],
                      ),
                      Row(
                        children: [
                          Text("IBOV: "),
                          Text(
                            percentFormatter.format(widget
                                .performance
                                .history[
                            widget.performance.history.length -
                                2]
                                .grossAmount /
                                widget.performance.grossAmount),
                            style: Theme.of(context)
                                .textTheme
                                .bodyText2
                                .copyWith(color: Colors.orange),
                          )
                        ],
                      ),
                    ],
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
//
// class MonthRentability extends StatelessWidget {
//   final double portfolioRentability;
//   final double cdiRentability;
//   final double ibovRentability;
//
//   const MonthRentability(
//       {Key key,
//       this.portfolioRentability,
//       this.cdiRentability,
//       this.ibovRentability})
//       : super(key: key);
//
//   @override
//   Widget build(BuildContext context) {
//     return Column(
//       children: <Widget>[
//         Row(
//           mainAxisAlignment: MainAxisAlignment.spaceBetween,
//           children: <Widget>[
//             _buildRentabilityRow(
//                 constants.PORTFOLIO_LABEL, portfolioRentability, Colors.blue),
//             _buildRentabilityRow(
//                 constants.CDI_LABEL, cdiRentability, Colors.purple),
//             _buildRentabilityRow(
//                 constants.IBOV_LABEL, ibovRentability, Colors.deepOrange),
//           ],
//         )
//       ],
//     );
//   }
//
//   Row _buildRentabilityRow(String label, double rentability, Color color) {
//     return Row(
//       children: <Widget>[
//         Text(label),
//         Text(
//           ' ${percentFormatter.format(rentability)}',
//           style: TextStyle(color: color),
//         ),
//       ],
//     );
//   }
// }
//
// class MonthTotals extends StatelessWidget {
//   final double total;
//   final double variation;
//
//   const MonthTotals(this.total, this.variation);
//
//   @override
//   Widget build(BuildContext context) {
//     return Container(
//       child: Column(
//         children: <Widget>[
//           Row(
//             mainAxisAlignment: MainAxisAlignment.spaceBetween,
//             children: <Widget>[
//               Text('Total bruto'),
//               Text(
//                 moneyFormatter.format(total),
//                 style: TextStyle(fontSize: 16.0),
//               ),
//             ],
//           ),
//           Row(
//             mainAxisAlignment: MainAxisAlignment.spaceBetween,
//             children: <Widget>[
//               Text('Variação no mês'),
//               Text(
//                 moneyFormatter.format(variation),
//                 style: TextStyle(
//                   color: variation >= 0 ? Colors.green : Colors.red,
//                   fontSize: 16.0,
//                 ),
//               ),
//             ],
//           ),
//         ],
//       ),
//     );
//   }
// }
