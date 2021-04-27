import 'dart:io';

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
      navigationBar: CupertinoNavigationBar(
        backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
      ),
      child: Padding(
        padding:
            Platform.isIOS ? EdgeInsets.zero : const EdgeInsets.only(top: 16.0),
        child: SettingsList(
          backgroundColor: Platform.isAndroid
              ? CupertinoTheme.of(context).scaffoldBackgroundColor
              : null,
          sections: [
            SettingsSection(
              title: "RENDA VARIÁVEL",
              tiles: [
                SettingsTile(
                  title: 'Importar automaticamente (CEI)',
                  titleTextStyle: CupertinoTheme.of(context)
                      .textTheme
                      .textStyle
                      .copyWith(fontWeight: FontWeight.normal, fontSize: 16),
                  onPressed: (context) =>
                      ModalUtils.showDragableModalBottomSheet(
                    context,
                    CeiLoginPage(
                        userService:
                            Provider.of<UserService>(context, listen: false)),
                  ),
                ),
                SettingsTile(
                  title: 'Operação de compra',
                  titleTextStyle: CupertinoTheme.of(context)
                      .textTheme
                      .textStyle
                      .copyWith(fontWeight: FontWeight.normal, fontSize: 16),
                  onPressed: (context) => goToInvestmentList(context, true),
                ),
                SettingsTile(
                  title: 'Operação de venda',
                  titleTextStyle: CupertinoTheme.of(context)
                      .textTheme
                      .textStyle
                      .copyWith(fontWeight: FontWeight.normal, fontSize: 16),
                  onPressed: (context) => goToInvestmentList(context, false),
                ),
              ],
            ),
            SettingsSection(
              tiles: [],
            ),
          ],
        ),
      ),
    );
  }
}
