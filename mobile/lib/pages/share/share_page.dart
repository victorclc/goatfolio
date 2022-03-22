import 'dart:io';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:goatfolio/bloc/loading/loading_state.dart';
import 'package:goatfolio/pages/share/friends_list.dart';
import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:goatfolio/services/friends/cubit/friends_rentability_cubit.dart';
import 'package:goatfolio/services/friends/model/friend_rentability.dart';
import 'package:goatfolio/utils/modal.dart' as modal;
import 'package:goatfolio/widgets/platform_aware_progress_indicator.dart';
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
          IconButton(
            alignment: Alignment.centerRight,
            icon: Icon(CupertinoIcons.person_add),
            color: CupertinoColors.activeBlue,
            onPressed: () => modal.showDraggableModalBottomSheet(
              context,
              FriendsListPage(
                userService: Provider.of<UserService>(context, listen: false),
              ),
            ),
          ),
        ],
        backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
      ),
      backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
      body: buildContent(context),
    );
  }

  Widget buildIos(BuildContext context) {
    return CupertinoPageScaffold(
      navigationBar: CupertinoNavigationBar(
        backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
        previousPageTitle: "",
        middle: Text("Compartilhar"),
        trailing: IconButton(
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
      ),
      child: buildContent(context),
    );
  }

  Widget buildContent(BuildContext context) {
    return SafeArea(
      child: Container(
        child: Column(
          children: [
            BlocBuilder<FriendsRentabilityCubit, LoadingState>(
              builder: (context, state) {
                if (state == LoadingState.LOADING) {
                  return PlatformAwareProgressIndicator();
                } else if (state == LoadingState.LOADED) {
                  return buildDayRanking(
                      context,
                      BlocProvider.of<FriendsRentabilityCubit>(context,
                              listen: true)
                          .rentabilityList!);
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
      BuildContext context, List<FriendRentability> friendsRentability) {
    return Container();
  }
}
