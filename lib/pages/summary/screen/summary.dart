import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/pages/summary/widget/highest_highs_card.dart';
import 'package:goatfolio/pages/summary/widget/lowest_lows_card.dart';
import 'package:goatfolio/pages/summary/widget/month_summary_card.dart';
import 'package:goatfolio/services/performance/model/portfolio_performance.dart';
import 'package:goatfolio/services/performance/notifier/portfolio_performance_notifier.dart';
import 'package:intl/intl.dart';
import 'package:goatfolio/common/extension/string.dart';
import 'package:provider/provider.dart';

class SummaryPage extends StatefulWidget {
  static const title = 'Resumo';
  static const icon = Icon(CupertinoIcons.chart_bar_square_fill);

  @override
  _SummaryPageState createState() => _SummaryPageState();
}

class _SummaryPageState extends State<SummaryPage> {
  PortfolioPerformance performance;

  Widget build(BuildContext context) {
    return CustomScrollView(
      slivers: [
        CupertinoSliverNavigationBar(
          largeTitle: Text(SummaryPage.title),
          leading: Text(
            DateFormat("MMMM yyyy", 'pt_BR')
                .format(DateTime.now())
                .capitalize(),
            style: Theme
                .of(context)
                .textTheme
                .subtitle2
                .copyWith(fontWeight: FontWeight.w400),
          ),
          trailing: CupertinoButton(
            padding: EdgeInsets.zero,
            child: Icon(
              CupertinoIcons.bell,
              color: Colors.black,
            ),
            onPressed: () => print("BELL"),
          ),
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
                  future: Provider
                      .of<PortfolioPerformanceNotifier>(context,
                      listen: true)
                      .future,
                  builder: (context, snapshot) {
                    switch (snapshot.connectionState) {
                      case ConnectionState.none:
                      case ConnectionState.active:
                        break;
                      case ConnectionState.waiting:
                        return CupertinoActivityIndicator();
                      case ConnectionState.done:
                        if (snapshot.hasData) {
                          performance = snapshot.data;
                          return Column(
                            children: [
                              MonthSummaryCard(performance),
                              HighestHighsCard(performance),
                              LowestLowsCard(performance),
                            ],
                          );
                        }
                    }
                    return Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        SizedBox(
                          height: 32,
                        ),
                        Text("Tivemos um problema ao carregar",
                            style: Theme
                                .of(context)
                                .textTheme
                                .subtitle1),
                        Text(" as informações.",
                            style: Theme
                                .of(context)
                                .textTheme
                                .subtitle1),
                        SizedBox(
                          height: 8,
                        ),
                        Text("Toque para tentar novamente.",
                            style: Theme
                                .of(context)
                                .textTheme
                                .subtitle1),
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
