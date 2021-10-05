import 'package:flutter/cupertino.dart';
import 'package:goatfolio/pages/portfolio/rgb.dart';
import 'package:goatfolio/pages/portfolio/stock_summary_item.dart';
import 'package:goatfolio/performance/model/stock_summary.dart';
import 'package:goatfolio/utils/formatters.dart';
import 'package:goatfolio/widgets/expansion_tile_custom.dart';

class InvestmentTypeExpansionTile extends StatelessWidget {
  final String title;
  final double grossAmount;
  final double totalAmount;
  final List<StockSummary> items;
  final Map<String, Rgb> colors;
  final bool initiallyExpanded;

  InvestmentTypeExpansionTile(
      {Key? key,
      required this.title,
      required this.grossAmount,
      required this.totalAmount,
      required this.items,
      required this.colors,
      this.initiallyExpanded = false})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;

    final sortedItems = items
      ..sort((a, b) => a.currentTickerName.compareTo(b.currentTickerName));

    return Padding(
      padding: const EdgeInsets.only(left: 8, right: 8),
      child: ExpansionTileCustom(
        initiallyExpanded: initiallyExpanded,
        childrenPadding: EdgeInsets.only(left: 8, right: 8),
        tilePadding: EdgeInsets.zero,
        title: Column(
          children: [
            Row(
              children: [
                Container(
                  width: 4,
                  height: 14,
                  color: colors.containsKey(title)
                      ? colors[title]!.toColor()
                      : Rgb.random().toColor(),
                ),
                Text(
                  ' ' + title,
                  style: textTheme.navTitleTextStyle,
                ),
              ],
            ),
          ],
        ),
        subtitle: Padding(
          padding: const EdgeInsets.only(top: 8, bottom: 8),
          child: Column(
            children: [
              Padding(
                padding: const EdgeInsets.only(left: 8, right: 8),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: <Widget>[
                    Row(
                      children: <Widget>[
                        Text(
                          "Total em carteira",
                          style: textTheme.textStyle.copyWith(fontSize: 16),
                        ),
                      ],
                    ),
                    Text(
                      moneyFormatter.format(grossAmount),
                      style: textTheme.textStyle.copyWith(fontSize: 16),
                    ),
                  ],
                ),
              ),
              Padding(
                padding: const EdgeInsets.only(left: 8, right: 8),
                child: Row(
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
                    // 100000 100
                    // 34000   x
                    Text(
                      percentFormatter.format(
                          totalAmount == 0 ? 0.0 : grossAmount / totalAmount),
                      style: textTheme.textStyle.copyWith(fontSize: 16),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        children: [
          SizedBox(
            height: 8,
          ),
          ListView.builder(
            padding: EdgeInsets.zero,
            physics: NeverScrollableScrollPhysics(),
            shrinkWrap: true,
            itemBuilder: (context, index) {
              final item = sortedItems[index];
              final Rgb rgb = colors[item.ticker]!;
              final color = rgb.toColor();

              return StockInvestmentSummaryItem(
                summary: item,
                color: color,
                portfolioTotalAmount: totalAmount,
                typeTotalAmount: grossAmount,
              );
            },
            itemCount: sortedItems.length,
          ),
        ],
      ),
    );
  }
}
