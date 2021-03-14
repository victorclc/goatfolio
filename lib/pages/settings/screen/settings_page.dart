import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/main.dart';
import 'package:goatfolio/pages/login/screen/login.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:provider/provider.dart';
import 'package:settings_ui/settings_ui.dart';

class SettingsPage extends StatelessWidget {
  static const String title = 'Configurações';
  static const Icon icon = Icon(CupertinoIcons.settings);

  @override
  Widget build(BuildContext context) {
    return CupertinoPageScaffold(
      navigationBar: CupertinoNavigationBar(
        middle: Text(title),
      ),
      child: SettingsList(
        sections: [
          SettingsSection(
            tiles: [
              SettingsTile(
                title: 'Sobre',
              ),
              SettingsTile(
                title: 'Sair',
                titleTextStyle:
                    TextStyle(fontSize: 16, color: Colors.redAccent),
                onPressed: (BuildContext context) async {
                  await Provider.of<UserService>(context, listen: false)
                      .signOut();
                  Navigator.of(context, rootNavigator: true).pushReplacement(
                      CupertinoPageRoute(
                          builder: (context) =>
                              LoginPage(onLoggedOn: goToNavigationPage)));
                },
              ),
            ],
          ),
        ],
      ),
    );
  }
}
