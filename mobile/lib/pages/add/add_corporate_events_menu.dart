import 'dart:io';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/pages/add/grouping_add.dart';
import 'package:goatfolio/pages/add/incorporation_add.dart';
import 'package:goatfolio/pages/add/name_change_add.dart';
import 'package:goatfolio/pages/add/split_add.dart';
import 'package:goatfolio/pages/add/stock_list.dart';
import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:provider/provider.dart';
import 'package:settings_ui/settings_ui.dart';
import 'package:goatfolio/utils/modal.dart' as modal;

void goToAddCorporateEventsMenu(BuildContext context) async {
  Navigator.of(context).push(
    MaterialPageRoute(
      builder: (context) => AddCorporateEventsMenu(),
    ),
  );
}

class AddCorporateEventsMenu extends StatelessWidget {
  static const String title = "Evento Corporativo";
  static const Color backgroundGray = Color(0xFFEFEFF4);

  const AddCorporateEventsMenu({Key? key}) : super(key: key);

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
        leading: BackButton(color: textColor),
        title: Text(
          title,
          style: TextStyle(color: textColor),
        ),
        backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
      ),
      backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
      body: buildContent(context),
    );
  }

  Widget buildIos(BuildContext context) {
    return CupertinoPageScaffold(
      navigationBar: CupertinoNavigationBar(
        middle: Text(title),
        backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
      ),
      child: buildContent(context),
    );
  }

  Widget buildContent(BuildContext context) {
    final userService = Provider.of<UserService>(context, listen: false);

    return SettingsList(
      sections: [
        SettingsSection(
          tiles: [
            SettingsTile(
              title: 'Grupamento',
              iosLikeTile: true,
              onPressed: (_) => goToInvestmentList(
                  context,
                  false,
                  userService,
                  (ticker) => modal.showDraggableModalBottomSheet(
                        context,
                        GroupingAdd(
                          title: "Grupamento",
                          ticker: ticker,
                          userService: userService,
                        ),
                      ),
                  title: "Grupamento"),
            ),
            SettingsTile(
              title: 'Desdobramento',
              iosLikeTile: true,
              onPressed: (_) => goToInvestmentList(
                context,
                false,
                userService,
                (ticker) => modal.showDraggableModalBottomSheet(
                  context,
                  SplitAdd(
                    title: "Desdobramento",
                    ticker: ticker,
                    userService: userService,
                  ),
                ),
                title: 'Desdobramento',
              ),
            ),
            SettingsTile(
              title: 'Incorporação',
              iosLikeTile: true,
              onPressed: (_) => goToInvestmentList(
                context,
                false,
                userService,
                (ticker) => modal.showDraggableModalBottomSheet(
                  context,
                  IncorporationAdd(
                    title: "Incorporação",
                    ticker: ticker,
                    userService: userService,
                  ),
                ),
                title: 'Incorporação',
              ),
            ),
            SettingsTile(
              title: 'Mudança de nome',
              iosLikeTile: true,
              onPressed: (_) => goToInvestmentList(
                context,
                false,
                userService,
                    (ticker) => modal.showDraggableModalBottomSheet(
                  context,
                  NameChangeAdd(
                    title: "Mudança de nome",
                    ticker: ticker,
                    userService: userService,
                  ),
                ),
                title: 'Mudança de nome',
              ),
            ),
          ],
        ),
        SettingsSection(
          tiles: [],
        ),
      ],
    );
  }
}
