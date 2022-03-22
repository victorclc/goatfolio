import 'dart:io';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:goatfolio/services/friends/cubit/friends_list_cubit.dart';
import 'package:goatfolio/services/friends/model/friend.dart';

void goToFriendsDetails(BuildContext context, Friend friend) {
  Navigator.of(context).push(
    MaterialPageRoute(
      builder: (context) => FriendDetails(friend: friend,),
    ),
  );
}

class FriendDetails extends StatefulWidget {
  final Friend friend;
  const FriendDetails({Key? key, required this.friend}) : super(key: key);

  @override
  _FriendDetailsState createState() => _FriendDetailsState();
}

class _FriendDetailsState extends State<FriendDetails> {
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
          "Detalhes",
          style: TextStyle(color: textColor),
        ),
        actions: [],
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
        middle: Text("Detalhes"),
      ),
      child: buildContent(context),
    );
  }

  Widget buildContent(BuildContext context) {
    return Column(
      children: [
        CupertinoButton(
          child: Text(
            "Remover Amigo",
            style: TextStyle(color: CupertinoColors.systemRed),
          ),
          onPressed: () => BlocProvider.of<FriendsListCubit>(context)
              .remove(context, widget.friend),
        )
      ],
    );
  }
}
