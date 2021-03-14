import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:settings_ui/settings_ui.dart';

class AddPrototypePage extends StatelessWidget {
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
                  style: CupertinoTheme.of(context).textTheme.navLargeTitleTextStyle,
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
                      ),
                      SettingsTile(
                        title: 'Operação de compra',
                      ),
                      SettingsTile(
                        title: 'Operação de venda',
                      ),
                    ],
                  ),
                  SettingsSection(tiles: [],),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
