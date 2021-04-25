import 'dart:io';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/main.dart';
import 'package:goatfolio/pages/login/screen/login.dart';
import 'package:goatfolio/pages/settings/screen/theme_page.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/investment/storage/stock_investment.dart';
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
      // backgroundColor: Colors.black,
      navigationBar: CupertinoNavigationBar(
        middle: Text(title),
        backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
      ),
      child: Column(
        children: [

          Expanded(
            child: SingleChildScrollView(
              child: SettingsList(
                shrinkWrap: true,
                physics: NeverScrollableScrollPhysics(),
                backgroundColor: Platform.isAndroid
                    ? CupertinoTheme.of(context)
                    .scaffoldBackgroundColor
                    : null,
                sections: [
                  SettingsSection(
                    tiles: [
                      SettingsTile(
                        titleTextStyle: CupertinoTheme.of(context).textTheme.textStyle.copyWith(fontWeight: FontWeight.normal, fontSize: 16),
                        title: 'Aparência',
                        onPressed: goToThemePage,
                      ),
                      SettingsTile(
                        titleTextStyle: CupertinoTheme.of(context).textTheme.textStyle.copyWith(fontWeight: FontWeight.normal, fontSize: 16),
                        title: 'Notificações',
                        onPressed: goToNotificationsPage,
                      ),
                      SettingsTile(
                        titleTextStyle: CupertinoTheme.of(context).textTheme.textStyle.copyWith(fontWeight: FontWeight.normal, fontSize: 16),
                        title: 'Sobre',
                        onPressed: goToAboutPage,
                      ),
                      SettingsTile(
                        titleTextStyle: CupertinoTheme.of(context).textTheme.textStyle.copyWith(fontWeight: FontWeight.normal, fontSize: 16),
                        title: 'Avalie-nos',
                        onPressed: (_) async => await LaunchReview.launch(),
                      ),
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
                  // SettingsSection(
                  //   tiles: [
                  //     SettingsTile(
                  //       title: 'Sair',
                  //       leading: Icon(
                  //         Icons.exit_to_app_rounded,
                  //         color: Colors.redAccent,
                  //       ),
                  //       titleTextStyle:
                  //           TextStyle(fontSize: 16, color: Colors.redAccent),
                  //       onPressed: (BuildContext context) async {
                  //         final userService =
                  //             Provider.of<UserService>(context, listen: false);
                  //         await deleteInvestmentsDatabase();
                  //         await userService.signOut();
                  //         Navigator.of(context, rootNavigator: true).pushReplacement(
                  //           CupertinoPageRoute(
                  //             builder: (context) => LoginPage(
                  //               onLoggedOn: goToNavigationPage,
                  //               userService: userService,
                  //             ),
                  //           ),
                  //         );
                  //       },
                  //     ),
                  //   ],
                  // )
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
