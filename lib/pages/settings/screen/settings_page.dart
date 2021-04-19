import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/main.dart';
import 'package:goatfolio/pages/login/screen/login.dart';
import 'package:goatfolio/pages/settings/screen/theme_page.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/investment/storage/stock_investment.dart';
import 'package:provider/provider.dart';
import 'package:settings_ui/settings_ui.dart';
import 'package:url_launcher/url_launcher.dart';

import 'about_page.dart';

class SettingsPage extends StatelessWidget {
  static const String title = 'Configurações';
  static const Icon icon = Icon(CupertinoIcons.settings);
  final String _contactUrl = 'mailto:contato@goatfolio.com.br?subject=Teste&body=Isso%20eh%20uma%20mensagem%20de%20teste';

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
                title: 'Contato',
                onPressed: (_) => _launchURL(),
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

  void _launchURL() async =>
      await canLaunch(_contactUrl) ? await launch(_contactUrl) : throw 'Could not launch $_contactUrl';
}
