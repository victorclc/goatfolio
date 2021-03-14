import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/common/util/dialog.dart';
import 'package:goatfolio/common/util/modal.dart';
import 'package:goatfolio/common/widget/multi_prompt.dart';
import 'package:goatfolio/pages/add/prompt/cei_authentication.dart';
import 'package:goatfolio/pages/add/screen/stock_list_prototype.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/vandelay/client/client.dart';
import 'package:provider/provider.dart';
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
                        onPressed: (context)  =>
                            ModalUtils.showUnDismissibleModalBottomSheet(
                                context,
                                MultiPrompt(
                                  onSubmit: (Map values) async {
                                    final client = VandelayClient(Provider.of<UserService>(context, listen: false));
                                    try {
                                      await client.importCEIRequest(
                                          values['username'], values['password']);
                                      await DialogUtils.showSuccessDialog(
                                          context, "Importação solicitada com sucesso!");
                                    } catch (Exception) {
                                      await DialogUtils.showErrorDialog(
                                          context, "Erro ao solicitar importação, tente novamente mais tarde.");
                                    }

                                  },
                                  promptRequests: [
                                    CeiTaxIdPrompt(),
                                    CeiPasswordPrompt()
                                  ],
                                )),
                      ),
                      SettingsTile(
                        title: 'Operação de compra',
                        onPressed: (context) => goToInvestmentListPrototype(context, true),
                      ),
                      SettingsTile(
                        title: 'Operação de venda',
                        onPressed: (context) => goToInvestmentListPrototype(context, false),
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
