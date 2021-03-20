import 'package:flutter/cupertino.dart';

class StockAdd extends StatefulWidget {
  @override
  _StockAddState createState() => _StockAddState();
}

const BoxDecoration _kDefaultRoundedBorderDecoration = BoxDecoration(
  color: CupertinoDynamicColor.withBrightness(
    color: CupertinoColors.white,
    darkColor: CupertinoColors.black,
  ),
  border: _kDefaultRoundedBorder,
  borderRadius: BorderRadius.all(Radius.circular(5.0)),
);

const Border _kDefaultRoundedBorder = Border(
  // top: _kDefaultRoundedBorderSide,
  bottom: _kDefaultRoundedBorderSide,
  left: _kDefaultRoundedBorderSide,
  right: _kDefaultRoundedBorderSide,
);

const BorderSide _kDefaultRoundedBorderSide = BorderSide(
  color: CupertinoDynamicColor.withBrightness(
    color: Color(0x33000000),
    darkColor: Color(0x33FFFFFF),
  ),
  style: BorderStyle.solid,
  width: 0.0,
);
class _StockAddState extends State<StockAdd> {
  @override
  Widget build(BuildContext context) {
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
                textInputAction: TextInputAction.next,
                keyboardType: TextInputType.text,
                prefix: Container(
                  width: 120,
                  padding: EdgeInsets.all(16),
                  child: Text(
                    'Ativo  ',
                    style: textTheme.textStyle
                        .copyWith(fontWeight: FontWeight.w400),
                  ),
                ),
                placeholder: "ex.: BIDI4",
              ),
              CupertinoTextField(
                onChanged: (something) {
                  setState(() {});
                },
                textInputAction: TextInputAction.next,
                keyboardType: TextInputType.text,
                prefix: Container(
                  width: 120,
                  padding: EdgeInsets.all(16),
                  child: Text(
                    'Corretora',
                    style: textTheme.textStyle
                        .copyWith(fontWeight: FontWeight.w400),
                  ),
                ),
                placeholder: "Corretora (opcional)",
              ),
              CupertinoTextField(
                onChanged: (something) {
                  setState(() {});
                },
                decoration: BoxDecoration(),
                textInputAction: TextInputAction.next,
                keyboardType: TextInputType.number,
                prefix: Container(
                  width: 120,
                  padding: EdgeInsets.all(16),
                  child: Text(
                    'Quantidade',
                    style: textTheme.textStyle
                        .copyWith(fontWeight: FontWeight.w400),
                  ),
                ),
                placeholder: "Quantidade",
              ),
              CupertinoTextField(
                onChanged: (something) {
                  setState(() {});
                },
                textInputAction: TextInputAction.next,
                keyboardType: TextInputType.numberWithOptions(decimal: true),
                prefix: Container(
                  width: 118,
                  padding: EdgeInsets.all(16),
                  child: Text(
                    'Preço ',
                    style: textTheme.textStyle
                        .copyWith(fontWeight: FontWeight.w400),
                  ),
                ),
                placeholder: "Preço",
              ),
              CupertinoTextField(
                onChanged: (something) {
                  setState(() {});
                },
                decoration: BoxDecoration(),
                textInputAction: TextInputAction.next,
                keyboardType: TextInputType.number,
                prefix: Container(
                  width: 120,
                  padding: EdgeInsets.all(16),
                  child: Text(
                    'Data',
                    style: textTheme.textStyle
                        .copyWith(fontWeight: FontWeight.w400),
                  ),
                ),
                placeholder: "dd/mm/aaaa",
              ),
              CupertinoTextField(
                onChanged: (something) {
                  setState(() {});
                },
                textInputAction: TextInputAction.next,
                keyboardType: TextInputType.numberWithOptions(decimal: true),
                prefix: Container(
                  width: 120,
                  padding: EdgeInsets.all(16),
                  child: Text(
                    'Custos',
                    style: textTheme.textStyle
                        .copyWith(fontWeight: FontWeight.w400),
                  ),
                ),
                placeholder: "Custos (opcional)",
              ),
            ],
          ),
        ));
  }
}
