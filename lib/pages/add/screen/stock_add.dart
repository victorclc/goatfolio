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
          leading: CupertinoButton(
            padding: EdgeInsets.all(0),
            child: Align(
              alignment: AlignmentDirectional.centerStart,
              widthFactor: 1.0,
              child: Text(
                'Cancelar',
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ),
            onPressed: () => Navigator.of(context).pop(),
          ),
          middle: Text(
            'Nova compra',
            style: textTheme.navTitleTextStyle,
          ),
        ),
        child: SingleChildScrollView(
          child: Column(
            children: [
              SizedBox(height: 32,),
              CupertinoTextField(
                onChanged: (something) {
                  setState(() {});
                },
                decoration: BoxDecoration(),
                autofillHints: [AutofillHints.username],
                textInputAction: TextInputAction.next,
                keyboardType: TextInputType.number,
                prefix: Container(
                  width: 115,
                  padding: EdgeInsets.all(16),
                  child: Text(
                    'Ativo  ',
                    style: textTheme.textStyle
                        .copyWith(fontWeight: FontWeight.w400),
                  ),
                ),
                placeholder: "Obrigatório",
              ),
              CupertinoTextField(
                onChanged: (something) {
                  setState(() {});
                },
                decoration: BoxDecoration(),
                autofillHints: [AutofillHints.username],
                textInputAction: TextInputAction.next,
                keyboardType: TextInputType.number,
                prefix: Container(
                  width: 115,
                  padding: EdgeInsets.all(16),
                  child: Text(
                    'Corretora',
                    style: textTheme.textStyle
                        .copyWith(fontWeight: FontWeight.w400),
                  ),
                ),
                placeholder: "Obrigatório",
              ),
              CupertinoTextField(
                onChanged: (something) {
                  setState(() {});
                },
                decoration: BoxDecoration(),
                autofillHints: [AutofillHints.username],
                textInputAction: TextInputAction.next,
                keyboardType: TextInputType.number,
                prefix: Container(
                  width: 115,
                  padding: EdgeInsets.all(16),
                  child: Text(
                    'Quantidade',
                    style: textTheme.textStyle
                        .copyWith(fontWeight: FontWeight.w400),
                  ),
                ),
                placeholder: "Obrigatório",
              ),
              CupertinoTextField(
                onChanged: (something) {
                  setState(() {});
                },
                decoration: BoxDecoration(),
                autofillHints: [AutofillHints.username],
                textInputAction: TextInputAction.next,
                keyboardType: TextInputType.number,
                prefix: Container(
                  width: 115,
                  padding: EdgeInsets.all(16),
                  child: Text(
                    'Preço  ',
                    style: textTheme.textStyle
                        .copyWith(fontWeight: FontWeight.w400),
                  ),
                ),
                placeholder: "Obrigatório",
              ),
              CupertinoTextField(
                onChanged: (something) {
                  setState(() {});
                },
                decoration: BoxDecoration(),
                autofillHints: [AutofillHints.username],
                textInputAction: TextInputAction.next,
                keyboardType: TextInputType.number,
                prefix: Container(
                  width: 115,
                  padding: EdgeInsets.all(16),
                  child: Text(
                    'Data',
                    style: textTheme.textStyle
                        .copyWith(fontWeight: FontWeight.w400),
                  ),
                ),
                placeholder: "Obrigatório",
              ),
              CupertinoTextField(
                onChanged: (something) {
                  setState(() {});
                },
                decoration: BoxDecoration(),
                autofillHints: [AutofillHints.username],
                textInputAction: TextInputAction.next,
                keyboardType: TextInputType.number,
                prefix: Container(
                  width: 115,
                  padding: EdgeInsets.all(16),
                  child: Text(
                    'Custos',
                    style: textTheme.textStyle
                        .copyWith(fontWeight: FontWeight.w400),
                  ),
                ),
                placeholder: "Obrigatório",
              ),
            ],
          ),
        ));
  }
}
