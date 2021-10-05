import 'dart:io';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:goatfolio/bloc/loading/loading_state.dart';
import 'package:goatfolio/global.dart' as global;
import 'package:goatfolio/pages/summary/highest_highs_card.dart';
import 'package:goatfolio/pages/summary/lowest_lows_card.dart';
import 'package:goatfolio/pages/summary/rentability_card.dart';
import 'package:goatfolio/performance/cubit/summary_cubit.dart';
import 'package:goatfolio/theme/theme_changer.dart';
import 'package:goatfolio/widgets/loading_error.dart';

import 'package:goatfolio/widgets/platform_aware_progress_indicator.dart';
import 'package:provider/provider.dart';

class SummaryPage extends StatelessWidget {
  static const title = 'Resumo';
  static const icon = Icon(CupertinoIcons.chart_bar_square_fill);
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();

  Widget build(BuildContext context) {
    return BlocConsumer<SummaryCubit, LoadingState>(
      listener: (context, state) =>
          global.loadingStateObservers.forEach((o) => o.listen(context, state)),
      builder: (context, state) {
        final cubit = BlocProvider.of<SummaryCubit>(context);
        if (Platform.isIOS) {
          return buildIos(context, cubit, state);
        }
        return buildAndroid(context, cubit, state);
      },
    );
  }

  Widget buildAndroid(
      BuildContext context, SummaryCubit cubit, LoadingState state) {
    return Scaffold(
      key: _scaffoldKey,
      // drawer: buildDrawer(),
      body: CupertinoTheme(
        data: Provider.of<ThemeChanger>(context).themeData,
        child: RefreshIndicator(
          onRefresh: cubit.refresh,
          child: buildContent(context, cubit, state),
        ),
      ),
    );
  }

  Widget buildIos(
      BuildContext context, SummaryCubit cubit, LoadingState state) {
    return Scaffold(
      key: _scaffoldKey,
      // drawer: buildDrawer(),
      body: buildContent(context, cubit, state),
    );
  }

  Widget buildContent(
      BuildContext context, SummaryCubit cubit, LoadingState state) {
    return CustomScrollView(
      slivers: [
        CupertinoSliverNavigationBar(
          heroTag: 'summaryNavBar',
          largeTitle: Text(SummaryPage.title),
          border: null,
          backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
        ),
        if (Platform.isIOS)
          CupertinoSliverRefreshControl(onRefresh: cubit.refresh),
        SliverSafeArea(
          top: false,
          sliver: SliverPadding(
            padding: EdgeInsets.symmetric(vertical: 12),
            sliver: SliverList(
              delegate: SliverChildListDelegate.fixed(
                [
                  Builder(
                    builder: (_) {
                      if (state == LoadingState.LOADING &&
                          cubit.portfolioSummary == null) {
                        return PlatformAwareProgressIndicator();
                      } else if (state == LoadingState.LOADED ||
                          cubit.portfolioSummary != null) {
                        return Column(
                          children: [
                            RentabilityCard(cubit.portfolioSummary!),
                            Row(
                              children: [
                                Expanded(
                                  child: HighestHighsCard(
                                      cubit.portfolioSummary!.tickerVariation),
                                ),
                                Expanded(
                                    child: LowestLowsCard(cubit
                                        .portfolioSummary!.tickerVariation)),
                              ],
                            ),
                          ],
                        );
                      } else {
                        return LoadingError(onRefreshPressed: cubit.refresh);
                      }
                    },
                  ),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }
}
