import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/pages/login/screen/login.dart';
import 'package:goatfolio/pages/navigation/screen/navigation.dart';
import 'package:goatfolio/pages/settings/screen/theme_page.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/investment/storage/stock_investment.dart';
import 'package:goatfolio/services/notification/client/notification.dart';
import 'package:launch_review/launch_review.dart';
import 'package:provider/provider.dart';
import 'package:settings_ui/settings_ui.dart';

import 'about_page.dart';
import 'notifications_page.dart';

class SettingsPage extends StatelessWidget {
  static const String title = 'Configurações';
  static const Icon icon = Icon(CupertinoIcons.settings);

  @override
  Widget build(BuildContext context) {
    return CupertinoPageScaffold(
      navigationBar: CupertinoNavigationBar(
        middle: Text(title),
        backgroundColor: CupertinoTheme
            .of(context)
            .scaffoldBackgroundColor,
      ),
      child: SettingsList(
        sections: [
          SettingsSection(
            tiles: [
              SettingsTile(
                title: 'Aparência',
                onPressed: goToThemePage,
              ),
              SettingsTile(
                title: 'Notificações',
                onPressed: goToNotificationsPage,
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
                titleTextStyle:
                TextStyle(fontSize: 16, color: Colors.redAccent),
                onPressed: (BuildContext context) async {
                  final userService =
                  Provider.of<UserService>(context, listen: false);
                  await deleteInvestmentsDatabase();
                  await NotificationClient(userService).unregisterToken(
                      await FirebaseMessaging.instance.getToken());
                  await userService.signOut();
                  Navigator.of(context, rootNavigator: true).pushReplacement(
                    CupertinoPageRoute(
                      builder: (context) =>
                          LoginPage(
                            onLoggedOn: goToNavigationPage,
                            userService: userService,
                          ),
                    ),
                  );
                },
              ),
            ],
          )
        ],
      ),
    );
  }
}
