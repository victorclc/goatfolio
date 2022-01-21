import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';

class HelpPage extends StatelessWidget {
  const HelpPage({Key? key}) : super(key: key);

  Widget buildAndroid(BuildContext context) {
    final textColor =
        CupertinoTheme.of(context).textTheme.navTitleTextStyle.color;
    return Scaffold(
      appBar: AppBar(
        leading: BackButton(
          color: textColor,
        ),
        title: Text(
          "Pêndencias",
          style: TextStyle(color: textColor),
        ),
        backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
      ),
      backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
      body: buildContent(context),
    );
  }

  Widget buildIos(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;
    return CupertinoPageScaffold(
      navigationBar: CupertinoNavigationBar(
        border: null,
        backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
        leading: CupertinoButton(
          padding: EdgeInsets.all(0),
          child: Align(
            alignment: AlignmentDirectional.centerStart,
            widthFactor: 1.0,
            child: Text(
              'Voltar',
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ),
          onPressed: () => Navigator.of(context).pop(),
        ),
        middle: Text(
          "Ajuda",
          style: textTheme.navTitleTextStyle,
        ),
      ),
      child: buildContent(context),
    );
  }

  @override
  Widget build(BuildContext context) {
    return buildIos(context);
  }

  Widget buildContent(BuildContext context) {
    return Container(
      child: Column(
        children: [
          ExpansionTile(
            title: Text("O que é uma pêndencia de importacão?"),
            children: [
              Container(
                padding: EdgeInsets.only(left: 16, right: 16, bottom: 16),
                alignment: Alignment.centerLeft,
                child: Text("É uma pendencia drr"),
              ),
            ],
          ),
          ExpansionTile(
            title: Text("Por que preciso fornecer o preco médio"),
            children: [
              Container(
                padding: EdgeInsets.only(left: 16, right: 16, bottom: 16),
                alignment: Alignment.centerLeft,
                child: Text("Por que sim zéquinha."),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
