import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

class CeiLoginPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;
    return CupertinoPageScaffold(
        navigationBar: CupertinoNavigationBar(
          backgroundColor: Colors.transparent,
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
          trailing: CupertinoButton(
            padding: EdgeInsets.all(0),
            child: Align(
              alignment: AlignmentDirectional.centerStart,
              widthFactor: 1.0,
              child: Text(
                'Seguinte',
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ),
            onPressed: () => Navigator.of(context).pop(),
          ),
        ),
        child: SafeArea(
            child: SingleChildScrollView(
          child: Column(
            children: [
              Container(
                alignment: Alignment.center,
                padding: EdgeInsets.only(top: 16, bottom: 16),
                child: Text('Importação CEI',
                    style: textTheme.navLargeTitleTextStyle
                        .copyWith(fontWeight: FontWeight.w400)),
              ),
              Container(
                alignment: Alignment.center,
                padding: EdgeInsets.only(left: 16, right: 16),
                child: Text(
                  'Entre com os dados de acesso da conta que deseja realizar a importação',
                  style: textTheme.textStyle,
                  textAlign: TextAlign.center,
                ),
              ),
              SizedBox(
                height: 48,
              ),
              CupertinoTextField(
                autofillHints: [AutofillHints.username],
                prefix: Container(
                  width: 100,
                  padding: EdgeInsets.all(16),
                  child: Text(
                    'CPF  ',
                    style: textTheme.textStyle
                        .copyWith(fontWeight: FontWeight.w400),
                  ),
                ),
                placeholder: "Obrigatório",
              ),
              CupertinoTextField(
                autofillHints: [AutofillHints.password],
                obscureText: true,
                prefix: Container(
                  padding: EdgeInsets.all(16),
                  width: 100,
                  child: Text(
                    'Senha',
                    style: textTheme.textStyle
                        .copyWith(fontWeight: FontWeight.w400),
                  ),
                ),
                placeholder: "Obrigatório",
              ),
              CupertinoButton(
                child: Text("Esqueceu sua senha?"),
                onPressed: () async => await launch('https://cei.b3.com.br/CEI_Responsivo/recuperar-senha.aspx'),
              ),
              SizedBox(
                height: 48,
              ),
              Container(
                alignment: Alignment.center,
                padding: EdgeInsets.only(left: 16, right: 16),
                child: Text(
                  'Limitações da importação',
                  style: textTheme.textStyle,
                  textAlign: TextAlign.center,
                ),
              ),
              SizedBox(
                height: 16,
              ),
              Icon(Icons.info_outline),
              SizedBox(
                height: 8,
              ),
              Container(
                alignment: Alignment.center,
                padding: EdgeInsets.only(left: 16, right: 16),
                child: Text(
                  'O CEI disponibiliza apenas as movimentações dos ultimos 18 meses. Caso você tenha movimentações anteriores a esse período, será necessario inclui-las manualmente, para que voce tenha os valores corretos da rentabilidade da sua carteira',
                  style: textTheme.textStyle
                      .copyWith(fontSize: 12, fontWeight: FontWeight.w200),
                  textAlign: TextAlign.center,
                ),
              ),
            ],
          ),
        )));
  }
}
