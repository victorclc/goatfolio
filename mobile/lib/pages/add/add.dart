import 'dart:io';

import 'package:badges/badges.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:goatfolio/pages/add/stock_list.dart';
import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:goatfolio/services/stock/stock_divergence_cubit.dart';
import 'package:goatfolio/utils/modal.dart' as modal;

import 'package:provider/provider.dart';
import 'package:settings_ui/settings_ui.dart';

import 'cei_login.dart';
import 'cei_pendency.dart';

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

    return BlocBuilder<StockDivergenceCubit, DivergenceState>(
        builder: (context, state) {
      return SettingsList(
        sections: [
          SettingsSection(
            title: "RENDA VARIÁVEL",
            tiles: [
              if (state == DivergenceState.HAS_DIVERGENCE)
                SettingsTile(
                  title: 'Pendências importação (CEI)',
                  iosLikeTile: true,
                  onPressed: (_) => modal.showDraggableModalBottomSheet(
                      context, CeiPendency()),
                  // onPressed: (_) => Navigator.of(context).push(
                  //   MaterialPageRoute(builder: (context) => CeiPendency()),
                  // ),
                  trailing: SizedBox(
                    width: 100,
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: <Widget>[
                        Badge(
                          elevation: 0,
                          shape: BadgeShape.circle,
                          padding: EdgeInsets.all(7),
                          badgeContent: Text(
                            '${BlocProvider.of<StockDivergenceCubit>(context).divergences.length}',
                            style: TextStyle(color: Colors.white),
                          ),
                        ),
                        Padding(
                          padding: const EdgeInsets.only(left: 20),
                          child: Icon(
                            CupertinoIcons.forward,
                            size: 21.0,
                            color: Color(0xFFC7C7CC),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              SettingsTile(
                title: 'Importar automaticamente (CEI)',
                iosLikeTile: true,
                onPressed: (_) => modal.showDraggableModalBottomSheet(
                  context,
                  CeiLoginPage(userService: userService),
                ),
              ),
              SettingsTile(
                title: 'Operação de compra',
                iosLikeTile: true,
                onPressed: (_) => goToInvestmentList(
                  context,
                  true,
                  userService,
                ),
              ),
              SettingsTile(
                title: 'Operação de venda',
                iosLikeTile: true,
                onPressed: (_) => goToInvestmentList(
                  context,
                  false,
                  userService,
                ),
              ),
            ],
          ),
          SettingsSection(
            tiles: [],
          ),
        ],
      );
    });
  }
}
