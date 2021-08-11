import 'dart:io';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/common/util/modal.dart';
import 'package:goatfolio/pages/add/screen/stock_list.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/performance/notifier/portfolio_performance_notifier.dart';
import 'package:provider/provider.dart';
import 'package:settings_ui/settings_ui.dart';

import 'cei_login.dart';

class AddPage extends StatelessWidget {
  static const icon = Icon(Icons.add);
  static const String title = "Adicionar";
  static const Color backgroundGray = Color(0xFFEFEFF4);

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
          title: "RENDA VARIÁVEL",
          tiles: [
            SettingsTile(
              title: 'Importar automaticamente (CEI)',
              iosLikeTile: true,
              onPressed: (context) => ModalUtils.showDragableModalBottomSheet(
                context,
                CeiLoginPage(userService: userService),
              ),
            ),
            SettingsTile(
              title: 'Operação de compra',
              iosLikeTile: true,
              onPressed: (context) => goToInvestmentList(
                context,
                true,
                userService,
                Provider.of<PortfolioListNotifier>(context, listen: false)
                    .futureList,
              ),
            ),
            SettingsTile(
              title: 'Operação de venda',
              iosLikeTile: true,
              onPressed: (context) => goToInvestmentList(
                context,
                false,
                userService,
                Provider.of<PortfolioListNotifier>(context, listen: false)
                    .futureList,
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
