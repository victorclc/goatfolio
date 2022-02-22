import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:goatfolio/bloc/loading/loading_state.dart';
import 'package:goatfolio/pages/share/friend_add.dart';
import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:goatfolio/services/friends/cubit/friends_cubit.dart';
import 'package:goatfolio/services/friends/model/friend.dart';
import 'package:goatfolio/services/friends/model/friends_list.dart';
import 'package:goatfolio/utils/modal.dart' as modal;
import 'package:goatfolio/widgets/platform_aware_progress_indicator.dart';

const Color mediumGrayColor = Color(0xFFC7C7CC);
const defaultCupertinoForwardIcon = Icon(
  CupertinoIcons.forward,
  size: 21.0,
  color: mediumGrayColor,
);

class FriendsListPage extends StatefulWidget {
  final UserService userService;

  const FriendsListPage({Key? key, required this.userService})
      : super(key: key);

  @override
  _FriendsListPageState createState() => _FriendsListPageState();
}

class _FriendsListPageState extends State<FriendsListPage> {
  @override
  Widget build(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;
    return CupertinoPageScaffold(
      navigationBar: CupertinoNavigationBar(
        border: null,
        backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
        leading: CupertinoButton(
          padding: EdgeInsets.all(0),
          child: Align(
            alignment: AlignmentDirectional.centerStart,
            widthFactor: 1.0,
            child: Text(
              'OK',
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ),
          onPressed: () => Navigator.of(context).pop(),
        ),
        middle: Text(
          "Compartilhar",
          style: textTheme.navTitleTextStyle,
        ),
        trailing: IconButton(
          alignment: Alignment.centerRight,
          icon: Icon(CupertinoIcons.add),
          color: CupertinoColors.activeBlue,
          onPressed: () => modal.showDraggableModalBottomSheet(
            context,
            FriendAdd(
              userService: widget.userService,
            ),
          ),
        ),
      ),
      child: SafeArea(
        child: Container(
          child: Column(
            children: [
              BlocBuilder<FriendsCubit, LoadingState>(
                builder: (context, state) {
                  if (state == LoadingState.LOADING) {
                    return PlatformAwareProgressIndicator();
                  } else if (state == LoadingState.LOADED) {
                    return buildFriendsList(
                        BlocProvider.of<FriendsCubit>(context).friendsList!,
                        textTheme);
                  } else {
                    return Container();
                  }
                },
              ),
            ],
          ),
        ),
      ),

      // Padding(
      //   padding: const EdgeInsets.all(16.0),
      //   child: Column(
      //     crossAxisAlignment: CrossAxisAlignment.start,
      //     children: [
      //       Text(
      //         "COMPARTILHANDO COM",
      //         style: textTheme.tabLabelTextStyle,
      //       ),
      //       Container(
      //         padding: EdgeInsets.only(top: 16),
      //         child: Center(child: Text("Ninguém.")),
      //       )
      //     ],
      //   ),
      // ),
    );
  }

  Widget buildFriendsList(
      FriendsList friendsList, CupertinoTextThemeData textTheme) {
    return Container(
      padding: EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                child: Text(
                  "COMPARTILHANDO COM",
                  style: textTheme.tabLabelTextStyle.copyWith(fontSize: 12),
                ),
              ),
            ]..addAll(buildFriends(friendsList.friends, textTheme)),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                child: Text(
                  "CONVITES",
                  style: textTheme.tabLabelTextStyle.copyWith(fontSize: 12),
                ),
              ),
            ]..addAll(buildFriends(friendsList.requests, textTheme)),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                child: Text(
                  "CONVIDADO(A)",
                  style: textTheme.tabLabelTextStyle.copyWith(fontSize: 12),
                ),
              ),
            ]..addAll(buildFriends(friendsList.invites, textTheme)),
          ),
        ],
      ),
    );
  }

  List<Container> buildFriends(
      List<Friend> friends, CupertinoTextThemeData textTheme) {
    List<Container> friendsWidget = [];

    friends.forEach((element) {
      friendsWidget.add(
        Container(
          padding: EdgeInsets.only(top: 8),
          child: CupertinoButton(
            padding: EdgeInsets.zero,
            child: Column(
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      element.user.name,
                      style: textTheme.textStyle,
                    ),
                    defaultCupertinoForwardIcon
                  ],
                ),
                Divider()
              ],
            ),
            onPressed: () => 1,
          ),
        ),
      );
    });
    return friendsWidget;
  }
}
