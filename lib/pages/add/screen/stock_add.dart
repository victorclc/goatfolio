import 'package:flutter/cupertino.dart';

class StockAdd extends StatefulWidget {
  @override
  _StockAddState createState() => _StockAddState();
}

class _StockAddState extends State<StockAdd> {
  @override
  Widget build(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;
    return CupertinoPageScaffold(
        navigationBar: CupertinoNavigationBar(
          backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
          border: null,
          middle: Text(
            'Nova compra',
            style: textTheme.navTitleTextStyle,
          ),
        ),
        child: Column(
          children: [
            CupertinoTextField(
              placeholder: 'Ativo',
              padding: EdgeInsets.all(16),
            ),
            CupertinoTextField(
              placeholder: 'Quantidade',
              padding: EdgeInsets.all(16),
            ),
            CupertinoTextField(
              placeholder: 'Preço',
              padding: EdgeInsets.all(16),
            ),
            CupertinoTextField(
              placeholder: 'Data',
              padding: EdgeInsets.all(16),
            ),
            CupertinoTextField(
              placeholder: 'Custos',
              padding: EdgeInsets.all(16),
            ),
            CupertinoTextField(
              placeholder: 'Corretora',
              padding: EdgeInsets.all(16),
            ),
          ],
        ));
  }
}
