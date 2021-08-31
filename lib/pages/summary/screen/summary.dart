import 'dart:io';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/common/theme/theme_changer.dart';
import 'package:goatfolio/pages/summary/widget/highest_highs_card.dart';
import 'package:goatfolio/pages/summary/widget/lowest_lows_card.dart';
import 'package:goatfolio/pages/summary/widget/rentability_card.dart';
import 'package:goatfolio/services/performance/model/portfolio_summary.dart';
import 'package:goatfolio/services/performance/notifier/portfolio_performance_notifier.dart';
import 'package:goatfolio/services/performance/notifier/portfolio_summary_notifier.dart';
import 'package:provider/provider.dart';

class SummaryPage extends StatefulWidget {
  static const title = 'Resumo';
  static const icon = Icon(CupertinoIcons.chart_bar_square_fill);
  final Function() openDrawerCb;

  const SummaryPage({Key key, @required this.openDrawerCb}) : super(key: key);

  @override
  _SummaryPageState createState() => _SummaryPageState();
}

class _SummaryPageState extends State<SummaryPage> {
  PortfolioSummary summary;
  GlobalKey<ScaffoldState> _key = GlobalKey<ScaffoldState>();

  void initState() {
    Provider.of<PortfolioListNotifier>(context, listen: false);
    super.initState();
  }

  Future<void> onRefresh() async {
    Provider.of<PortfolioListNotifier>(context, listen: false)
        .updatePerformance();
    await Provider.of<PortfolioSummaryNotifier>(context, listen: false)
        .updatePerformance();
  }

  Widget build(BuildContext context) {
    if (Platform.isIOS) {
      return buildIos(context);
    }
    return buildAndroid(context);
  }

  Widget buildAndroid(BuildContext context) {
    return Scaffold(
      body: CupertinoTheme(
        data: Provider.of<ThemeChanger>(context).themeData,
        child: RefreshIndicator(
          onRefresh: onRefresh,
          child: buildScrollView(context),
        ),
      ),
    );
  }

  Widget buildIos(BuildContext context) {
    return buildScrollView(context);
  }

  Widget buildScrollView(BuildContext context) {
    return CustomScrollView(
      slivers: [
        CupertinoSliverNavigationBar(
          leading: GestureDetector(
            child: Icon(
              Icons.menu,
              color: CupertinoTheme.of(context).textTheme.textStyle.color,
              size: 24,
            ),
            onTap: widget.openDrawerCb,
          ),
          heroTag: 'summaryNavBar',
          largeTitle: Text(SummaryPage.title),
          backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
          border: null,
        ),
        if (Platform.isIOS)
          CupertinoSliverRefreshControl(onRefresh: () async {
            Provider.of<PortfolioListNotifier>(context, listen: false)
                .updatePerformance();
            await Provider.of<PortfolioSummaryNotifier>(context, listen: false)
                .updatePerformance();
          }),
        SliverSafeArea(
          top: false,
          sliver: SliverPadding(
            padding: EdgeInsets.symmetric(vertical: 12),
            sliver: SliverList(
              delegate: SliverChildListDelegate.fixed([
                FutureBuilder(
                  future: Provider.of<PortfolioSummaryNotifier>(context,
                          listen: true)
                      .futureSummary,
                  builder: (context, snapshot) {
                    switch (snapshot.connectionState) {
                      case ConnectionState.none:
                      case ConnectionState.active:
                        break;
                      case ConnectionState.waiting:
                        return Platform.isIOS
                            ? CupertinoActivityIndicator()
                            : Center(
                                child:
                                    Center(child: CircularProgressIndicator()));
                      case ConnectionState.done:
                        if (snapshot.hasData) {
                          summary = snapshot.data;
                          return Column(
                            children: [
                              RentabilityCard(summary),
                              Row(
                                children: [
                                  Expanded(
                                      child: HighestHighsCard(
                                          summary.stocksVariation)),
                                  Expanded(
                                      child: LowestLowsCard(
                                          summary.stocksVariation)),
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
                        Text(" as informações.", style: textTheme.textStyle),
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
                            Provider.of<PortfolioSummaryNotifier>(context,
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
}
