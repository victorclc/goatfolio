import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/common/util/modal.dart';
import 'package:goatfolio/pages/add/screen/stock_list.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/performance/notifier/portfolio_performance_notifier.dart';
import 'package:provider/provider.dart';
import 'package:settings_ui/settings_ui.dart';

import 'cei_login.dart';

class AddPage extends StatelessWidget {
  static const icon = Icon(Icons.add);
  static const String title = "Adicionar";
  static const Color backgroundGray = Color(0xFFEFEFF4);

  @override
  Widget build(BuildContext context) {
    final userService = Provider.of<UserService>(context, listen: false);
    return CupertinoPageScaffold(
      navigationBar: CupertinoNavigationBar(
        middle: Text(title),
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
                  CeiLoginPage(userService: userService),
                ),
              ),
              SettingsTile(
                title: 'Operação de compra',
                onPressed: (context) => goToInvestmentList(
                  context,
                  true,
                  userService,
                  Provider.of<PortfolioListNotifier>(context, listen: false)
                      .futureList,
                ),
              ),
              SettingsTile(
                title: 'Operação de venda',
                onPressed: (context) => goToInvestmentList(
                  context,
                  false,
                  userService,
                  Provider.of<PortfolioListNotifier>(context, listen: false)
                      .futureList,
                ),
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
