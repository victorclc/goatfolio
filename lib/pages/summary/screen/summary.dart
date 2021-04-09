import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/pages/summary/widget/highest_highs_card.dart';
import 'package:goatfolio/pages/summary/widget/lowest_lows_card.dart';
import 'package:goatfolio/pages/summary/widget/rentability_card.dart';
import 'package:goatfolio/services/performance/model/portfolio_summary.dart';
import 'package:goatfolio/services/performance/notifier/portfolio_performance_notifier.dart';
import 'package:provider/provider.dart';

class SummaryPage extends StatefulWidget {
  static const title = 'Resumo';
  static const icon = Icon(CupertinoIcons.chart_bar_square_fill);

  @override
  _SummaryPageState createState() => _SummaryPageState();
}

class _SummaryPageState extends State<SummaryPage> {
  PortfolioSummary summary;

  void initState() {
    super.initState();
  }

  Widget build(BuildContext context) {
    return CustomScrollView(
      slivers: [
        CupertinoSliverNavigationBar(
          largeTitle: Text(SummaryPage.title),
          backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
          border: null,
        ),
        CupertinoSliverRefreshControl(
          onRefresh: () async =>
              Provider.of<PortfolioPerformanceNotifier>(context, listen: false)
                  .updatePerformance(),
        ),
        SliverSafeArea(
          top: false,
          sliver: SliverPadding(
            padding: EdgeInsets.symmetric(vertical: 12),
            sliver: SliverList(
              delegate: SliverChildListDelegate.fixed([
                FutureBuilder(
                  future: Provider.of<PortfolioPerformanceNotifier>(context,
                          listen: true)
                      .futureSummary,
                  builder: (context, snapshot) {
                    switch (snapshot.connectionState) {
                      case ConnectionState.none:
                      case ConnectionState.active:
                        break;
                      case ConnectionState.waiting:
                        return CupertinoActivityIndicator();
                      case ConnectionState.done:
                        if (snapshot.hasData) {
                          summary = snapshot.data;
                          print(summary);
                          return Column(
                            children: [
                              RentabilityCard(summary),
                              Row(
                                children: [
                                  Expanded(child: HighestHighsCard(summary.stocksVariation)),
                                  Expanded(child: LowestLowsCard(summary.stocksVariation)),
                                ],
                              ),
                            ],
                          );
                        }
                    }
                    final textTheme = CupertinoTheme.of(context).textTheme;
                    return Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        SizedBox(
                          height: 32,
                        ),
                        Text("Tivemos um problema ao carregar",
                            style: textTheme.textStyle),
                        Text(" as informações.",
                            style: textTheme.textStyle),
                        SizedBox(
                          height: 8,
                        ),
                        Text("Toque para tentar novamente.",
                            style: textTheme.textStyle),
                        CupertinoButton(
                          padding: EdgeInsets.all(0),
                          child: Icon(
                            Icons.refresh_outlined,
                            size: 32,
                          ),
                          onPressed: () {
                            Provider.of<PortfolioPerformanceNotifier>(context,
                                    listen: false)
                                .updatePerformance();
                          },
                        ),
                      ],
                    );
                  },
                ),
              ]),
            ),
          ),
        ),
      ],
    );
  }

// Future<PortfolioPerformance> getPortfolioPerformance() async {
//   performance = await client.getPortfolioPerformance();
//   return performance;
// }
}
