import 'dart:io';

import 'package:app_settings/app_settings.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/navigation.dart';
import 'package:goatfolio/pages/login/login.dart';
import 'package:goatfolio/pages/settings/theme_page.dart';
import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:goatfolio/services/investment/storage/stock_investment.dart';
import 'package:goatfolio/services/notification/notification.dart';

import 'package:launch_review/launch_review.dart';
import 'package:provider/provider.dart';
import 'package:settings_ui/settings_ui.dart';

import 'about_page.dart';

class SettingsPage extends StatelessWidget {
  static const String title = 'Configurações';
  static const Icon icon = Icon(CupertinoIcons.settings);

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
    return SettingsList(
      sections: [
        SettingsSection(
          tiles: [
            SettingsTile(
              title: 'Aparência',
              subtitle: Platform.isAndroid
                  ? 'Modo escuro, claro ou automático'
                  : null,
              onPressed: goToThemePage,
            ),
            SettingsTile(
              title: 'Notificações',
              subtitle: Platform.isAndroid
                  ? 'Controle como você recebe as notificações'
                  : null,
              onPressed: (_) => AppSettings.openNotificationSettings(),
            ),
            SettingsTile(
              title: 'Sobre',
              onPressed: goToAboutPage,
            ),
            SettingsTile(
              title: 'Avalie-nos',
              onPressed: (_) async => await LaunchReview.launch(),
            ),
          ],
        ),
        SettingsSection(
          tiles: [
            SettingsTile(
              title: 'Sair',
              leading: Icon(
                Icons.exit_to_app_rounded,
                color: Colors.redAccent,
              ),
              titleTextStyle: TextStyle(fontSize: 16, color: Colors.redAccent),
              onPressed: (BuildContext context) async {
                final userService =
                    Provider.of<UserService>(context, listen: false);
                await deleteInvestmentsDatabase();
                await NotificationClient(userService).unregisterToken(
                    (await FirebaseMessaging.instance.getToken())!);
                await userService.signOut();
                Navigator.of(context, rootNavigator: true).pushReplacement(
                  CupertinoPageRoute(
                    builder: (context) => Scaffold(
                      body: LoginPage(
                        onLoggedOn: goToNavigationPage,
                        userService: userService,
                      ),
                    ),
                  ),
                );
              },
            ),
          ],
        )
      ],
    );
  }
}
