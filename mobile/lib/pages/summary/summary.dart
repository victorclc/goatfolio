import 'dart:io';

import 'package:badges/badges.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:goatfolio/bloc/loading/loading_state.dart';
import 'package:goatfolio/global.dart' as global;
import 'package:goatfolio/pages/settings/settings_page.dart';
import 'package:goatfolio/pages/share/share_page.dart';
import 'package:goatfolio/pages/summary/friends/friends_rantability_card.dart';
import 'package:goatfolio/pages/summary/high_low/highest_highs_card.dart';
import 'package:goatfolio/pages/summary/high_low/lowest_lows_card.dart';
import 'package:goatfolio/pages/summary/rentability/rentability_card.dart';
import 'package:goatfolio/services/friends/cubit/friends_list_cubit.dart';
import 'package:goatfolio/services/performance/cubit/summary_cubit.dart';
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
          trailing: BlocBuilder<FriendsListCubit, LoadingState>(
              builder: (context, state) {
            final cubit = BlocProvider.of<FriendsListCubit>(context);
            return Badge(
              padding: state == LoadingState.LOADED &&
                      cubit.friendsList!.requests.isNotEmpty
                  ? EdgeInsets.all(5)
                  : EdgeInsets.zero,
              position: BadgePosition.topEnd(top: 5, end: 5),
              child: IconButton(
                icon: Icon(CupertinoIcons.settings),
                onPressed: () => goToSettingsPage(context),
              ),
            );
          }),
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
