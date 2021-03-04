import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/add/prompt/cei_authentication.dart';
import 'package:goatfolio/add/screen/stock_list.dart';
import 'package:goatfolio/common/util/modal.dart';
import 'package:goatfolio/common/widget/multi_prompt.dart';

class AddPage extends StatelessWidget {
  static const icon = Icon(Icons.add);
  static const String title = "Adicionar";

  @override
  Widget build(BuildContext context) {
    return CupertinoPageScaffold(
      navigationBar: CupertinoNavigationBar(
        middle: Text(title),
      ),
      child: SafeArea(
        child: Container(
          child: Column(
            children: [
              Expanded(
                child: Column(
                  children: [
                    Expanded(
                      child: AddOptionButton(
                        icon: Icon(Icons.autorenew),
                        title: "Importar automaticamente",
                        subtitle: "Importe seus dados do portal CEI",
                        onPressed: () =>
                            ModalUtils.showUnDismissibleModalBottomSheet(
                                context,
                                MultiPrompt(
                                  onSubmit: (Map values) async => await 1,
                                  promptRequests: [
                                    CeiTaxIdPrompt(),
                                    CeiPasswordPrompt()
                                  ],
                                )),
                      ),
                    ),
                    Expanded(
                      child: AddOptionButton(
                        icon: Icon(Icons.trending_up),
                        title: "Operação de compra",
                        subtitle: "Cadastre suas aplicações em Renda Variável",
                        onPressed: () => goTInvestmentList(context, true),
                      ),
                    ),
                    Expanded(
                      child: AddOptionButton(
                        icon: Icon(Icons.trending_down),
                        includeBottomBorder: false,
                        title: "Operação de venda",
                        subtitle:
                            "Cadastre suas vendas/resgates de seus produtos cadastrados",
                        onPressed: () => goTInvestmentList(context, false),
                      ),
                    ),
                  ],
                ),
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [],
              )
            ],
          ),
        ),
      ),
    );
  }
}

class AddOptionButton extends StatelessWidget {
  final Icon icon;
  final String title;
  final String subtitle;
  final Function onPressed;
  final bool includeBottomBorder;

  const AddOptionButton(
      {Key key,
      this.icon,
      this.title,
      this.subtitle,
      this.onPressed,
      this.includeBottomBorder = true})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      decoration: this.includeBottomBorder
          ? BoxDecoration(
              border: Border(
                bottom: BorderSide(color: Colors.grey),
              ),
            )
          : null,
      child: CupertinoButton(
        padding: EdgeInsets.only(right: 8),
        onPressed: onPressed,
        child: Row(
          children: [
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: this.icon,
            ),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    this.title,
                    style: Theme.of(context)
                        .textTheme
                        .bodyText2
                        .copyWith(fontSize: 16, fontWeight: FontWeight.w500),
                  ),
                  Text(
                    this.subtitle,
                    style: Theme.of(context)
                        .textTheme
                        .bodyText2
                        .copyWith(fontSize: 16, fontWeight: FontWeight.w200),
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
