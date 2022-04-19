import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/pages/summary/rentability/rentability.dart';
import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:goatfolio/services/performance/model/portfolio_summary.dart';
import 'package:goatfolio/utils/formatters.dart';
import 'package:goatfolio/widgets/pressable_card.dart';
import 'package:provider/provider.dart';

class RentabilityCard extends StatefulWidget {
  static const String CARD_TITLE = "Rentabilidade";
  final PortfolioSummary summary;

  const RentabilityCard(this.summary, {Key? key}) : super(key: key);

  @override
  _RentabilityCardState createState() {
    return _RentabilityCardState();
  }
}

class _RentabilityCardState extends State<RentabilityCard> {
  @override
  Widget build(BuildContext context) {
    final userService = Provider.of<UserService>(context, listen: false);

    final textTheme = CupertinoTheme.of(context).textTheme;
    return Container(
      width: double.infinity,
      child: PressableCard(
        onPressed: () =>
            goToRentabilityPage(context, widget.summary, userService),
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
                      moneyFormatter.format(widget.summary.grossAmount),
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
                            style: textTheme.textStyle.copyWith(fontSize: 16),
                          ),
                          Text(
                            moneyFormatter
                                .format(widget.summary.monthVariation),
                            style: textTheme.textStyle.copyWith(
                                color: widget.summary.monthVariation >= 0
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
                            style: textTheme.textStyle.copyWith(fontSize: 16),
                          ),
                          Text(
                            moneyFormatter.format(widget.summary.dayVariation),
                            style: textTheme.textStyle.copyWith(
                                color: widget.summary.dayVariation >= 0
                                    ? Colors.green
                                    : Colors.red,
                                fontSize: 16),
                          ),
                        ],
                      ),
                    ],
                  ),
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
