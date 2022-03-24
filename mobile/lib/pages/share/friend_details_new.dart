import 'dart:io';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/services/friends/model/friend_rentability.dart';
import 'package:goatfolio/utils/formatters.dart';

void goToFriendsDetailsNew(
    BuildContext context, FriendRentability rentability) {
  Navigator.of(context).push(
    MaterialPageRoute(
      builder: (context) => FriendDetailsNew(
        rentability: rentability,
      ),
    ),
  );
}

class FriendDetailsNew extends StatefulWidget {
  final FriendRentability rentability;

  const FriendDetailsNew({Key? key, required this.rentability})
      : super(key: key);

  @override
  _FriendDetailsNewState createState() => _FriendDetailsNewState();
}

class _FriendDetailsNewState extends State<FriendDetailsNew> {
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
        middle: Text(widget.rentability.user.name),
      ),
      child: buildContent(context),
    );
  }

  Widget buildContent(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            alignment: Alignment.centerLeft,
            child: Text(
              "Valorização em",
              style: textTheme.navTitleTextStyle,
            ),
          ),
          SizedBox(
            height: 8,
          ),
          Text(
            'março de 2022',
            style: textTheme.tabLabelTextStyle.copyWith(fontSize: 16),
          ),
          Text(
            percentFormatter
                .format(widget.rentability.summary.monthVariationPerc / 100),
            style: textTheme.textStyle
                .copyWith(fontSize: 28, fontWeight: FontWeight.w500),
          ),
          Divider(),
          Text(
            '22 de março de 2022',
            style: textTheme.tabLabelTextStyle.copyWith(fontSize: 16),
          ),
          Text(
            percentFormatter
                .format(widget.rentability.summary.dayVariationPerc / 100),
            style: textTheme.textStyle
                .copyWith(fontSize: 28, fontWeight: FontWeight.w500),
          ),
          Divider(),
          CupertinoButton(
              padding: EdgeInsets.zero,
              child: Text(
                "Remover Amigo",
                style: TextStyle(color: CupertinoColors.systemRed),
              ),
              onPressed: () => 1),
          Text("Você compartilha sua rentabilidade com ${widget.rentability.user.name} desde domingo, 6 de março de 2022")
        ],
      ),
    );
  }
}
