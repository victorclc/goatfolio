import 'dart:io';

import 'package:badges/badges.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:goatfolio/bloc/loading/loading_state.dart';
import 'package:goatfolio/pages/share/friends_list.dart';
import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:goatfolio/services/friends/cubit/friends_list_cubit.dart';
import 'package:goatfolio/services/friends/cubit/friends_rentability_cubit.dart';
import 'package:goatfolio/services/friends/model/friend_rentability.dart';
import 'package:goatfolio/theme/helper.dart' as theme;
import 'package:goatfolio/utils/formatters.dart';
import 'package:goatfolio/utils/modal.dart' as modal;
import 'package:goatfolio/widgets/platform_aware_progress_indicator.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

void goToSharePage(BuildContext context) {
  Navigator.of(context).push(
    MaterialPageRoute(
      builder: (context) => SharePage(),
    ),
  );
}

class SharePage extends StatefulWidget {
  const SharePage({Key? key}) : super(key: key);

  @override
  State<SharePage> createState() => _SharePageState();
}

class _SharePageState extends State<SharePage> {
  @override
  void initState() {
    BlocProvider.of<FriendsRentabilityCubit>(context).refresh();
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    if (Platform.isIOS) {
      return buildIos(context);
    }
    return buildAndroid(context);
  }

  Widget buildAndroid(BuildContext context) {
    final textColor =
        CupertinoTheme.of(context).textTheme.navTitleTextStyle.color;
    return Scaffold(
      appBar: AppBar(
        leading: BackButton(
          color: textColor,
        ),
        title: Text(
          "Compartilhar",
          style: TextStyle(color: textColor),
        ),
        actions: [
          BlocBuilder<FriendsListCubit, LoadingState>(
              builder: (context, state) {
            final cubit = BlocProvider.of<FriendsListCubit>(context);
            return Badge(
              padding: state == LoadingState.LOADED &&
                      cubit.friendsList!.requests.isNotEmpty
                  ? EdgeInsets.all(5)
                  : EdgeInsets.zero,
              position: BadgePosition.topEnd(top: 5, end: 5),
              child: IconButton(
                alignment: Alignment.centerRight,
                icon: Icon(CupertinoIcons.person_add),
                color: CupertinoColors.activeBlue,
                onPressed: () => modal.showDraggableModalBottomSheet(
                  context,
                  FriendsListPage(
                    userService:
                        Provider.of<UserService>(context, listen: false),
                  ),
                ),
              ),
            );
          }),
        ],
        backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
      ),
      backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
      body: RefreshIndicator(
        onRefresh: BlocProvider.of<FriendsRentabilityCubit>(context).refresh,
        child: SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            child: buildContent(context)),
      ),
    );
  }

  Widget buildIos(BuildContext context) {
    return CupertinoPageScaffold(
      backgroundColor: theme.currentBrightness(context) == Brightness.light
          ? CupertinoTheme.of(context).barBackgroundColor
          : CupertinoTheme.of(context).scaffoldBackgroundColor,
      navigationBar: CupertinoNavigationBar(
        backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
        previousPageTitle: "",
        middle: Text("Compartilhar"),
        trailing: BlocBuilder<FriendsListCubit, LoadingState>(
            builder: (context, state) {
          final cubit = BlocProvider.of<FriendsListCubit>(context);
          return Badge(
            padding: state == LoadingState.LOADED &&
                    cubit.friendsList!.requests.isNotEmpty
                ? EdgeInsets.all(5)
                : EdgeInsets.zero,
            position: BadgePosition.topEnd(top: 5, end: -6),
            child: IconButton(
              alignment: Alignment.centerRight,
              padding: EdgeInsets.all(0),
              icon: Icon(CupertinoIcons.person_add_solid),
              onPressed: () => modal.showDraggableModalBottomSheet(
                context,
                FriendsListPage(
                  userService: Provider.of<UserService>(context, listen: false),
                ),
              ),
            ),
          );
        }),
      ),
      child: CustomScrollView(
        slivers: [
          CupertinoSliverRefreshControl(
            onRefresh:
                BlocProvider.of<FriendsRentabilityCubit>(context).refresh,
          ),
          SliverToBoxAdapter(
            child: buildContent(context),
          ),
        ],
      ),
    );
  }

  Widget buildContent(BuildContext context) {
    return SafeArea(
      child: Container(
        child: Column(
          children: [
            BlocBuilder<FriendsRentabilityCubit, LoadingState>(
              builder: (context, state) {
                final rentabilityList =
                    BlocProvider.of<FriendsRentabilityCubit>(context,
                            listen: true)
                        .rentabilityList;
                if (state == LoadingState.LOADING && rentabilityList == null) {
                  return Padding(
                    padding: const EdgeInsets.only(top: 16.0),
                    child: PlatformAwareProgressIndicator(),
                  );
                } else if (state == LoadingState.LOADED ||
                    rentabilityList != null) {
                  return Column(
                    children: [
                      buildDayRanking(
                        context,
                        rentabilityList!,
                      ),
                      SizedBox(
                        height: 16,
                      ),
                      buildMonthRanking(context, rentabilityList),
                    ],
                  );
                } else {
                  return Container();
                }
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget buildDayRanking(
      BuildContext context, List<FriendRentability> pFriendsRentability) {
    final textTheme = CupertinoTheme.of(context).textTheme;

    final friendsRentability = [...pFriendsRentability];
    friendsRentability.sort((a, b) =>
        b.summary.dayVariationPerc.compareTo(a.summary.dayVariationPerc));
    int ranking = 1;
    List<Widget> rankingLines = [];
    friendsRentability.forEach((element) =>
        rankingLines.add(RankingLine(rentability: element, rank: ranking++)));

    return Padding(
      padding: const EdgeInsets.all(8.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: EdgeInsets.only(left: 8, right: 8, top: 8),
            child: Text(
              DateFormat("'Variação hoje,' dd 'de' MMMM 'de' yyyy", "pt-BR")
                  .format(
                DateTime.now(),
              ),
              style: textTheme.navTitleTextStyle,
            ),
          ),
          SizedBox(
            height: 16,
          ),
        ]..addAll(rankingLines),
      ),
    );
  }

  Widget buildMonthRanking(
      BuildContext context, List<FriendRentability> pFriendsRentability) {
    final textTheme = CupertinoTheme.of(context).textTheme;
    final friendsRentability = [...pFriendsRentability];
    friendsRentability.sort((a, b) =>
        b.summary.monthVariationPerc.compareTo(a.summary.monthVariationPerc));

    int ranking = 1;
    List<Widget> rankingLines = [];
    friendsRentability.forEach((element) => rankingLines.add(RankingLine(
          rentability: element,
          rank: ranking++,
          monthLine: true,
        )));

    return Padding(
      padding: const EdgeInsets.all(8.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.only(left: 8.0, right: 8.0),
            child: Text(
              DateFormat("'Variação em 'MMMM 'de' yyyy", "pt-BR").format(
                DateTime.now(),
              ),
              style: textTheme.navTitleTextStyle,
            ),
          ),
          SizedBox(
            height: 16,
          ),
          Column(
            children: rankingLines,
          )
        ],
      ),
    );
  }
}

class RankingLine extends StatelessWidget {
  final FriendRentability rentability;
  final int rank;
  final bool monthLine;

  const RankingLine(
      {Key? key,
      required this.rentability,
      required this.rank,
      this.monthLine = false})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;
    final variationPerc = monthLine
        ? rentability.summary.monthVariationPerc
        : rentability.summary.dayVariationPerc;
    return Card(
      color: theme.currentBrightness(context) == Brightness.light
          ? CupertinoTheme.of(context).scaffoldBackgroundColor
          : CupertinoTheme.of(context).barBackgroundColor,
      child: Padding(
        padding: const EdgeInsets.only(left: 8.0, right: 8.0),
        child: CupertinoButton(
          padding: EdgeInsets.zero,
          onPressed: () => 1, //goToFriendsDetailsNew(context, rentability),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Row(
                children: [
                  SizedBox(
                    width: 4,
                  ),
                  Text(
                    "$rank°",
                    style: textTheme.textStyle.copyWith(fontSize: 20),
                  ),
                  VerticalDivider(width: 16),
                  Expanded(
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          rentability.user.name,
                          style: textTheme.textStyle,
                        ),
                        Text(
                          (variationPerc >= 0 ? "+" : "") +
                              "${percentFormatter.format(variationPerc / 100)}",
                          style: textTheme.textStyle.copyWith(
                              color: variationPerc >= 0
                                  ? Colors.green
                                  : Colors.red,
                              fontSize: 18),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              // Divider()
            ],
          ),
        ),
      ),
    );
  }
}
