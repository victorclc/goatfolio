import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:progress_indicators/progress_indicators.dart';
import 'package:url_launcher/url_launcher.dart';

class TermsAcceptanceWidget extends StatefulWidget {
  final Function onAccepted;

  const TermsAcceptanceWidget({Key key, @required this.onAccepted})
      : super(key: key);

  @override
  _TermsAcceptanceWidgetState createState() => _TermsAcceptanceWidgetState();
}

class _TermsAcceptanceWidgetState extends State<TermsAcceptanceWidget> {
  bool lgpdBox;
  bool termsBox;
  bool processing;

  @override
  void initState() {
    lgpdBox = false;
    termsBox = false;
    processing = false;
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return CustomScrollView(
      slivers: [
        SliverFillRemaining(
          hasScrollBody: false,
          child: Column(
            // mainAxisAlignment: MainAxisAlignment.spaceBetween,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Center(
                child: Column(
                  children: [
                    SizedBox(height: 128),
                    Center(
                      child: Icon(Icons.shield),
                    ),
                    SizedBox(
                      height: 16,
                    ),
                    Text(
                      "Termos de uso",
                      style: CupertinoTheme.of(context)
                          .textTheme
                          .textStyle
                          .copyWith(fontWeight: FontWeight.bold),
                    ),
                    Text(
                      "e",
                      style: CupertinoTheme.of(context).textTheme.textStyle,
                    ),
                    Text(
                      "Política de privacidade",
                      style: CupertinoTheme.of(context)
                          .textTheme
                          .textStyle
                          .copyWith(fontWeight: FontWeight.bold),
                    ),
                    SizedBox(height: 16),
                  ],
                ),
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        TextButton(
                          style: ButtonStyle(
                              padding: MaterialStateProperty.all<EdgeInsets>(
                                  EdgeInsets.all(0))),
                          onPressed: () => _launchURL(
                              "https://goatfolio.app/docs/politica-de-privacidade.pdf"),
                          child: Text("Abrir política de privacidade."),
                        ),
                        TextButton(
                          style: ButtonStyle(
                              padding: MaterialStateProperty.all<EdgeInsets>(
                                  EdgeInsets.all(0))),
                          onPressed: () => _launchURL(
                              "https://goatfolio.app/docs/termos-de-uso.pdf"),
                          child: Text("Abrir termos de uso."),
                        ),
                      ],
                    ),
                  ),
                  CheckboxListTile(
                    controlAffinity: ListTileControlAffinity.leading,
                    value: lgpdBox,
                    onChanged: (value) {
                      setState(() {
                        lgpdBox = value;
                      });
                    },
                    title: Text(
                      "Autorizo o fornecimento dos dados e-mail e nome/apelido para a funcionalidade excluisiva do aplicativo e não autorizo o repasse dessas informações a terceiros.",
                      style: CupertinoTheme.of(context)
                          .textTheme
                          .textStyle
                          .copyWith(fontSize: 14),
                    ),
                  ),
                  CheckboxListTile(
                    controlAffinity: ListTileControlAffinity.leading,
                    value: termsBox,
                    onChanged: (value) {
                      setState(() {
                        termsBox = value;
                      });
                    },
                    title: Text(
                      "Li e aceito as política de privacidade e termos de uso.",
                      style: CupertinoTheme.of(context)
                          .textTheme
                          .textStyle
                          .copyWith(fontSize: 14),
                    ),
                  ),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      TextButton(
                          onPressed: () => Navigator.of(context).pop(),
                          child: Text("CANCELAR")),
                      ElevatedButton(
                        onPressed: lgpdBox && termsBox
                            ? () async {
                                if (!processing) {
                                  setState(() {
                                    processing = true;
                                  });
                                  await widget.onAccepted();
                                  setState(() {
                                    processing = false;
                                  });
                                }
                              }
                            : null,
                        child:
                            processing ? JumpingText("...") : Text("CONTINUAR"),
                      ),
                    ],
                  ),
                  SizedBox(
                    height: 16,
                  )
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }

  Future<void> _launchURL(String url) async =>
      await canLaunch(url) ? await launch(url) : throw 'Could not launch $url';
}
