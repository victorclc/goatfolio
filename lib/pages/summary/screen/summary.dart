import 'dart:io';

import 'package:badges/badges.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:goatfolio/common/bloc/loading/loading_state.dart';
import 'package:goatfolio/common/theme/theme_changer.dart';
import 'package:goatfolio/common/widget/loading_error.dart';
import 'package:goatfolio/common/widget/platform_aware_progress_indicator.dart';
import 'package:goatfolio/pages/summary/cubit/summary_cubit.dart';
import 'package:goatfolio/pages/summary/widget/highest_highs_card.dart';
import 'package:goatfolio/pages/summary/widget/lowest_lows_card.dart';
import 'package:goatfolio/pages/summary/widget/rentability_card.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:provider/provider.dart';

class SummaryContainer extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final userService = Provider.of<UserService>(context);

    return BlocProvider(
      create: (_) => SummaryCubit(userService),
      child: SummaryPage(),
    );
  }
}

class SummaryPage extends StatelessWidget {
  static const title = 'Resumo';
  static const icon = Icon(CupertinoIcons.chart_bar_square_fill);
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();

  Widget build(BuildContext context) {
    return BlocConsumer<SummaryCubit, LoadingState>(
      listener: (context, state) {},
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
      drawer: buildDrawer(),
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
      drawer: buildDrawer(),
      body: buildContent(context, cubit, state),
    );
  }

  Drawer buildDrawer() {
    return Drawer(
      child: ListView(
        children: [
          ListTile(title: Text('bagulho 1')),
          ListTile(title: Text('bagulho 2')),
        ],
      ),
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
          leading: Badge(
            padding: EdgeInsets.all(5.0), //EdgeInsets.zero,
            position: BadgePosition.topEnd(top: 10, end: -2),
            badgeContent: null,
            child: IconButton(
              constraints: BoxConstraints(),
              padding: EdgeInsets.only(left: 0),
              icon: Icon(
                Icons.menu,
                color: CupertinoTheme.of(context).textTheme.textStyle.color,
              ),
              onPressed: () => _scaffoldKey.currentState.openDrawer(),
            ),
          ),
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
                            RentabilityCard(cubit.portfolioSummary),
                            Row(
                              children: [
                                Expanded(
                                  child: HighestHighsCard(
                                      cubit.portfolioSummary.stocksVariation),
                                ),
                                Expanded(
                                    child: LowestLowsCard(cubit
                                        .portfolioSummary.stocksVariation)),
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
