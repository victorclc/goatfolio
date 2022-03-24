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
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          mainAxisAlignment: MainAxisAlignment.end,
          children: [
            IconButton(
              alignment: Alignment.centerRight,
              icon: Icon(CupertinoIcons.refresh),
              color: CupertinoColors.activeBlue,
              onPressed: () =>
                  BlocProvider.of<FriendsListCubit>(context).refresh(),
            ),
            IconButton(
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
          ],
        ),
      ),
      child: SafeArea(
        child: Container(
          child: Column(
            children: [
              BlocBuilder<FriendsListCubit, LoadingState>(
                builder: (context, state) {
                  if (state == LoadingState.LOADING) {
                    return Padding(
                      padding: const EdgeInsets.only(top: 16.0),
                      child: PlatformAwareProgressIndicator(),
                    );
                  } else if (state == LoadingState.LOADED) {
                    final friendsList =
                        BlocProvider.of<FriendsListCubit>(context, listen: true)
                            .friendsList!;
                    return Column(
                      children: [
                        if (friendsList.isEmpty())
                          Center(
                            child: Container(
                              padding:
                                  EdgeInsets.only(left: 64, right: 64, top: 16),
                              alignment: Alignment.center,
                              child: Text(
                                "Você ainda não compartilha a rentabilidade com ninguém.",
                                textAlign: TextAlign.center,
                                style: textTheme.tabLabelTextStyle
                                    .copyWith(fontSize: 16),
                              ),
                            ),
                          ),
                        buildFriendsList(friendsList, textTheme),
                        SizedBox(
                          height: 32,
                        ),
                        Container(
                          padding: EdgeInsets.only(left: 16, right: 16),
                          alignment: Alignment.centerLeft,
                          child: Text(
                            "Dados que são compartilhados com seus amigos:",
                            style: textTheme.navTitleTextStyle
                                .copyWith(fontSize: 14),
                          ),
                        ),
                        Container(
                          padding: EdgeInsets.only(left: 16, right: 16, top: 8),
                          alignment: Alignment.centerLeft,
                          child: Text(
                            "\t- Variação no dia (em %).\n\t- Variação mensal (em %).\n\t- Endereço de e-mail associado à sua conta.",
                            style: textTheme.textStyle.copyWith(fontSize: 14),
                          ),
                        )
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
                      onPressed: () =>
                          BlocProvider.of<FriendsListCubit>(context)
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

    friends.forEach(
      (element) {
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
                        child: AcceptDeclineTextButton(
                          onAcceptCb: () async =>
                              BlocProvider.of<FriendsListCubit>(context)
                                  .accept(context, element),
                          onDeclineCb: () async =>
                              BlocProvider.of<FriendsListCubit>(context)
                                  .decline(context, element),
                        )),
                  ],
                ),
                // Divider(),
              ],
            ),
          ),
        );
      },
    );
    return friendsWidget;
  }
}

class AcceptDeclineTextButton extends StatefulWidget {
  final Future<void> Function() onAcceptCb;
  final Future<void> Function() onDeclineCb;

  const AcceptDeclineTextButton({
    Key? key,
    required this.onAcceptCb,
    required this.onDeclineCb,
  }) : super(key: key);

  @override
  _AcceptDeclineTextButtonState createState() =>
      _AcceptDeclineTextButtonState();
}

class _AcceptDeclineTextButtonState extends State<AcceptDeclineTextButton> {
  bool processing = false;

  @override
  Widget build(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;

    return Row(
      children: [
        CupertinoButton(
          padding: EdgeInsets.all(0),
          onPressed: processing ? () => 1 : onDeclinePress,
          child: Text(
            "Recusar",
            style:
                textTheme.textStyle.copyWith(color: CupertinoColors.systemRed),
          ),
        ),
        SizedBox(
          width: 16,
        ),
        CupertinoButton(
          padding: EdgeInsets.all(0),
          onPressed: processing ? () => 1 : onAcceptPress,
          child: Text(
            "Aceitar",
            style: textTheme.textStyle
                .copyWith(color: CupertinoColors.systemGreen),
          ),
        ),
      ],
    );
  }

  void onAcceptPress() async {
    setState(() {
      processing = true;
    });
    await widget.onAcceptCb();
    setState(() {
      processing = false;
    });
  }

  void onDeclinePress() async {
    setState(() {
      processing = true;
    });
    await widget.onDeclineCb();
    setState(() {
      processing = false;
    });
  }
}
