import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/main.dart';
import 'package:goatfolio/pages/login/screen/login.dart';
import 'package:goatfolio/pages/settings/screen/theme_page.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/investment/storage/stock_investment.dart';
import 'package:provider/provider.dart';
import 'package:settings_ui/settings_ui.dart';

import 'about_page.dart';

class SettingsPage extends StatelessWidget {
  static const String title = 'Configurações';
  static const Icon icon = Icon(CupertinoIcons.settings);

  @override
  Widget build(BuildContext context) {
    return CupertinoPageScaffold(
      navigationBar: CupertinoNavigationBar(
        middle: Text(title),
        backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
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
                title: 'Sobre',
                onPressed: goToAboutPage,
              ),
              SettingsTile(
                title: 'Sair',
                titleTextStyle:
                    TextStyle(fontSize: 16, color: Colors.redAccent),
                onPressed: (BuildContext context) async {
                  final userService =
                      Provider.of<UserService>(context, listen: false);
                  await deleteInvestmentsDatabase();
                  await userService.signOut();
                  Navigator.of(context, rootNavigator: true).pushReplacement(
                    CupertinoPageRoute(
                      builder: (context) => LoginPage(
                        onLoggedOn: goToNavigationPage,
                        userService: userService,
                      ),
                    ),
                  );
                },
              ),
            ],
          ),
        ],
      ),
    );
  }
}
