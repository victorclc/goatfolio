import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:goatfolio/bloc/loading/loading_state.dart';
import 'package:goatfolio/pages/share/friend_add.dart';
import 'package:goatfolio/pages/share/friend_details.dart';
import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:goatfolio/services/friends/cubit/friends_list_cubit.dart';
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
  void initState() {
    BlocProvider.of<FriendsListCubit>(context).refresh();
    super.initState();
  }

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
              BlocBuilder<FriendsListCubit, LoadingState>(
                builder: (context, state) {
                  if (state == LoadingState.LOADING) {
                    return PlatformAwareProgressIndicator();
                  } else if (state == LoadingState.LOADED) {
                    return buildFriendsList(
                        BlocProvider.of<FriendsListCubit>(context, listen: true).friendsList!,
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
              if (friendsList.requests.isNotEmpty)
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      child: Text(
                        "AGUARDANDO SUA RESPOSTA",
                        style:
                            textTheme.tabLabelTextStyle.copyWith(fontSize: 12),
                      ),
                    ),
                  ]..addAll(buildRequests(friendsList.requests, textTheme)),
                ),
              if (friendsList.friends.isNotEmpty)
                Container(
                  child: Text(
                    "COMPARTILHANDO COM",
                    style: textTheme.tabLabelTextStyle.copyWith(fontSize: 12),
                  ),
                ),
            ]..addAll(buildFriends(friendsList.friends, textTheme)),
          ),
          if (friendsList.invites.isNotEmpty)
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  child: Text(
                    "CONVIDADO(A)",
                    style: textTheme.tabLabelTextStyle.copyWith(fontSize: 12),
                  ),
                ),
              ]..addAll(buildInvites(friendsList.invites, textTheme)),
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
            onPressed: () => goToFriendsDetails(context, element),
          ),
        ),
      );
    });
    return friendsWidget;
  }

  List<Container> buildInvites(
      List<Friend> friends, CupertinoTextThemeData textTheme) {
    List<Container> friendsWidget = [];

    friends.forEach((element) {
      friendsWidget.add(
        Container(
          padding: EdgeInsets.only(top: 8),
          child: Column(
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    element.user.email,
                    style: textTheme.textStyle,
                  ),
                  CupertinoButton(
                      padding: EdgeInsets.all(0),
                      onPressed: () => BlocProvider.of<FriendsListCubit>(context)
                          .cancel(context, element),
                      child: Text(
                        "Cancelar",
                        style: textTheme.textStyle
                            .copyWith(color: CupertinoColors.systemOrange),
                      )),
                ],
              ),
              // Divider(),
            ],
          ),
        ),
      );
    });
    return friendsWidget;
  }

  List<Container> buildRequests(
      List<Friend> friends, CupertinoTextThemeData textTheme) {
    List<Container> friendsWidget = [];

    friends.forEach((element) {
      friendsWidget.add(
        Container(
          padding: EdgeInsets.only(top: 8, bottom: 8),
          child: Column(
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Flexible(
                    flex: 5,
                    child: Text(
                      element.user.email + "",
                      style: textTheme.textStyle,
                    ),
                  ),
                  Flexible(
                    flex: 3,
                    child: Row(
                      children: [
                        CupertinoButton(
                          padding: EdgeInsets.all(0),
                          onPressed: () =>
                              BlocProvider.of<FriendsListCubit>(context)
                                  .decline(context, element),
                          child: Text(
                            "Recusar",
                            style: textTheme.textStyle
                                .copyWith(color: CupertinoColors.systemRed),
                          ),
                        ),
                        SizedBox(
                          width: 16,
                        ),
                        CupertinoButton(
                          padding: EdgeInsets.all(0),
                          onPressed: () =>
                              BlocProvider.of<FriendsListCubit>(context)
                                  .accept(context, element),
                          child: Text(
                            "Aceitar",
                            style: textTheme.textStyle
                                .copyWith(color: CupertinoColors.systemGreen),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              // Divider(),
            ],
          ),
        ),
      );
    });
    return friendsWidget;
  }
}
