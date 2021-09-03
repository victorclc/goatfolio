import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/common/formatter/brazil.dart';
import 'package:goatfolio/common/util/dialog.dart';
import 'package:goatfolio/common/util/modal.dart';
import 'package:goatfolio/common/widget/progress_indicator_scaffold.dart';
import 'package:goatfolio/services/authentication/service/cognito.dart';
import 'package:goatfolio/services/vandelay/service/vandelay_service.dart';
import 'package:goatfolio/services/vandelay/storage/import_history.dart';
import 'package:url_launcher/url_launcher.dart';

class CeiLoginPage extends StatefulWidget {
  final UserService userService;

  const CeiLoginPage({Key key, this.userService}) : super(key: key);

  @override
  _CeiLoginPageState createState() => _CeiLoginPageState();
}

class _CeiLoginPageState extends State<CeiLoginPage> {
  TextEditingController _cpfController = new TextEditingController();
  TextEditingController _passwordController = new TextEditingController();
  VandelayService service;
  Future _future;

  bool canSubmit() {
    return _cpfController.text.isNotEmpty &&
        _passwordController.text.isNotEmpty;
  }

  Future submitRequest() async {
    _future =
        service.importCEIRequest(_cpfController.text, _passwordController.text);
    return _future;
  }

  @override
  void initState() {
    super.initState();
    service = VandelayService(widget.userService);
  }

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
            onPressed: canSubmit()
                ? () => ModalUtils.showUnDismissibleModalBottomSheet(
                      context,
                      ProgressIndicatorScaffold(
                          message: 'Solicitando importação...',
                          future: submitRequest(),
                          onFinish: () async {
                            try {
                              await _future;
                              await DialogUtils.showSuccessDialog(context,
                                  "Agora é só esperar que te avisaremos quando o processo estiver concluído");
                            } catch (Exceptions) {
                              await DialogUtils.showErrorDialog(context,
                                  "Erro ao solicitar importação, tente novamente mais tarde.");
                            }

                            Navigator.of(context).pop();
                          }),
                    )
                : null,
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
                controller: _cpfController,
                onChanged: (something) {
                  setState(() {});
                },
                autofillHints: [AutofillHints.username],
                textInputAction: TextInputAction.next,
                keyboardType: TextInputType.number,
                inputFormatters: [cpfInputFormatter],
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
                controller: _passwordController,
                onChanged: (something) {
                  setState(() {});
                },
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
                onPressed: () async => await launch(
                    'https://cei.b3.com.br/CEI_Responsivo/recuperar-senha.aspx'),
              ),
              SizedBox(
                height: 48,
              ),
              _LimitationsInfo(),
            ],
          ),
        )));
  }
}

class _LimitationsInfo extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;
    return Column(
      children: [
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
    );
  }
}
