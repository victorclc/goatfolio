import 'dart:io';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/common/helper/theme_helper.dart';
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
    if (Platform.isIOS) {
      return buildIos(context);
    }
    return buildAndroid(context);
  }

  @override
  Widget buildAndroid(BuildContext context) {
    return CupertinoPageScaffold(
      backgroundColor:
          CupertinoThemeHelper.currentBrightness(context) == Brightness.light
              ? Color(0xFFEFEFF4)
              : CupertinoTheme.of(context).scaffoldBackgroundColor,
      navigationBar: CupertinoNavigationBar(
        backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
      ),
      child: SafeArea(
        child: Container(
          width: double.infinity,
          padding: Platform.isIOS
              ? EdgeInsets.zero
              : const EdgeInsets.only(top: 16.0),
          child: Column(
            children: [
              Platform.isAndroid
                  ? Container(
                      decoration: BoxDecoration(
                        color:
                            CupertinoThemeHelper.currentBrightness(context) ==
                                    Brightness.light
                                ? backgroundGray
                                : CupertinoTheme.of(context)
                                    .scaffoldBackgroundColor,
                      ),
                      padding: EdgeInsets.only(
                        left: 15.0,
                        right: 15.0,
                        bottom: 6.0,
                        top: 6,
                      ),
                      width: double.infinity,
                      child: Text(
                        'RENDA VARIÁVEL',
                        style: TextStyle(
                          color: Theme.of(context).accentColor,
                          fontWeight: FontWeight.bold,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                    )
                  : Container(),
              Expanded(
                child: SingleChildScrollView(
                  child: SettingsList(
                    shrinkWrap: true,
                    physics: NeverScrollableScrollPhysics(),
                    backgroundColor: Platform.isAndroid
                        ? CupertinoThemeHelper.currentBrightness(context) ==
                                Brightness.light
                            ? CupertinoTheme.of(context).scaffoldBackgroundColor
                            : Color.fromRGBO(28, 28, 30, 1)
                        : null,
                    sections: [
                      SettingsSection(
                        title: Platform.isIOS ? "RENDA VARIÁVEL" : null,
                        tiles: [
                          SettingsTile(
                            title: 'Importar automaticamente (CEI)',
                            titleTextStyle: CupertinoTheme.of(context)
                                .textTheme
                                .textStyle
                                .copyWith(
                                    fontWeight: FontWeight.normal,
                                    fontSize: 16),
                            onPressed: (context) =>
                                ModalUtils.showDragableModalBottomSheet(
                              context,
                              CeiLoginPage(
                                  userService: Provider.of<UserService>(context,
                                      listen: false)),
                            ),
                          ),
                          SettingsTile(
                            title: 'Operação de compra',
                            titleTextStyle: CupertinoTheme.of(context)
                                .textTheme
                                .textStyle
                                .copyWith(
                                    fontWeight: FontWeight.normal,
                                    fontSize: 16),
                            onPressed: (context) =>
                                goToInvestmentList(context, true),
                          ),
                          SettingsTile(
                            title: 'Operação de venda',
                            titleTextStyle: CupertinoTheme.of(context)
                                .textTheme
                                .textStyle
                                .copyWith(
                                    fontWeight: FontWeight.normal,
                                    fontSize: 16),
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
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget buildIos(BuildContext context) {
    return CupertinoPageScaffold(
      navigationBar: CupertinoNavigationBar(
        backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
      ),
      child: SettingsList(
        sections: [
          SettingsSection(
            title: "RENDA VARIÁVEL",
            tiles: [
              SettingsTile(
                title: 'Importar automaticamente (CEI)',
                onPressed: (context) => ModalUtils.showDragableModalBottomSheet(
                  context,
                  CeiLoginPage(
                      userService:
                          Provider.of<UserService>(context, listen: false)),
                ),
              ),
              SettingsTile(
                title: 'Operação de compra',
                onPressed: (context) => goToInvestmentList(context, true),
              ),
              SettingsTile(
                title: 'Operação de venda',
                onPressed: (context) => goToInvestmentList(context, false),
              ),
            ],
          ),
          SettingsSection(
            tiles: [],
          ),
        ],
      ),
    );
  }
}
