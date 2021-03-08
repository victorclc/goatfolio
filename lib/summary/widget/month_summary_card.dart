import 'package:flutter/material.dart';
import 'package:goatfolio/common/widget/pressable_card.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

class MonthSummaryCard extends StatefulWidget {
  static const String CARD_TITLE = "Rentabilidade";

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
              padding: const EdgeInsets.only(bottom: 16.0),
              child: Text("VAI TER COISA BOA AQUI"),
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
