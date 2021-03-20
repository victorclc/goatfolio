import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/common/util/modal.dart';
import 'package:goatfolio/pages/add/screen/stock_list.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:provider/provider.dart';
import 'package:settings_ui/settings_ui.dart';

import 'cei_login.dart';

class AddPage extends StatelessWidget {
  static const icon = Icon(Icons.add);
  static const String title = "Adicionar";
  static const Color backgroundGray = Color(0xFFEFEFF4);

  @override
  Widget build(BuildContext context) {
    return CupertinoPageScaffold(
      backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
      child: SafeArea(
        child: Column(
          children: [
            Container(
                padding: EdgeInsets.all(16),
                alignment: Alignment.centerLeft,
                child: DefaultTextStyle(
                  style: CupertinoTheme.of(context)
                      .textTheme
                      .navLargeTitleTextStyle,
                  child: Text(
                    title,
                  ),
                )),
            Expanded(
              child: SettingsList(
                shrinkWrap: true,
                physics: NeverScrollableScrollPhysics(),
                sections: [
                  SettingsSection(
                    title: "RENDA VARIÁVEL",
                    // subtitle: Text("RENDA VARIAVEL"),
                    // titlePadding: EdgeInsets.all(0),
                    // subtitlePadding: EdgeInsets.all(0),
                    tiles: [
                      SettingsTile(
                          title: 'Importar automaticamente (CEI)',
                          onPressed: (context) =>
                              // Navigator.of(context).push(
                              //   CupertinoPageRoute(
                              //       builder: (context) => CeiLoginPage()),
                              // ),
                              ModalUtils.showDragableModalBottomSheet(
                            context,
                                CeiLoginPage(userService: Provider.of<UserService>(context, listen: false)),
                          ),
                          ),
                      SettingsTile(
                        title: 'Operação de compra',
                        onPressed: (context) =>
                            goToInvestmentList(context, true),
                      ),
                      SettingsTile(
                        title: 'Operação de venda',
                        onPressed: (context) =>
                            goToInvestmentList(context, false),
                      ),
                    ],
                  ),
                  SettingsSection(
                    tiles: [],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
