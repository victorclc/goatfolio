import 'dart:io';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:goatfolio/services/authentication/cognito.dart';
import 'package:goatfolio/services/help/client/client.dart';
import 'package:goatfolio/services/help/model/faq.dart';
import 'package:goatfolio/services/help/model/faq_topic.dart';
import 'package:goatfolio/widgets/loading_error.dart';
import 'package:goatfolio/widgets/platform_aware_progress_indicator.dart';

void goCeiPendencyHelpPage(BuildContext context, UserService userService) {
  Navigator.of(context).push(
    MaterialPageRoute(
      builder: (context) => CeiPendencyHelpPage(
        userService: userService,
      ),
    ),
  );
}

class CeiPendencyHelpPage extends StatefulWidget {
  final UserService userService;

  const CeiPendencyHelpPage({Key? key, required this.userService})
      : super(key: key);

  @override
  _CeiPendencyHelpPageState createState() => _CeiPendencyHelpPageState();
}

class _CeiPendencyHelpPageState extends State<CeiPendencyHelpPage> {
  late HelpClient client;
  late Future<Faq> _future;

  @override
  void initState() {
    client = HelpClient(widget.userService);
    _future = client.getTopicFaq(FaqTopic.CEI_PENDENCY);
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    if (Platform.isIOS) {
      return buildIos(context);
    }
    return buildAndroid(context);
  }

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
    return CupertinoPageScaffold(
      navigationBar: CupertinoNavigationBar(
        backgroundColor: CupertinoTheme.of(context).scaffoldBackgroundColor,
        previousPageTitle: "",
        middle: Text("Pêndencias"),
      ),
      child: buildContent(context),
    );
  }

  Widget buildContent(BuildContext context) {
    final textTheme = CupertinoTheme.of(context).textTheme;

    return FutureBuilder(
      future: _future,
      builder: (context, snapshot) {
        switch (snapshot.connectionState) {
          case ConnectionState.none:
          case ConnectionState.active:
            break;
          case ConnectionState.waiting:
            return PlatformAwareProgressIndicator();
          case ConnectionState.done:
            if (!snapshot.hasData) {
              return Column(
                children: [
                  SizedBox(
                    height: 240,
                    child: Center(
                      child: Text(
                        "Nenhum dado encontrado.",
                        style: textTheme.textStyle,
                      ),
                    ),
                  ),
                ],
              );
            }
            Faq faq = snapshot.data! as Faq;

            return Container(
              child: Column(
                children: faq.questions
                    .map(
                      (question) => ExpansionTile(
                        title: Text(question.question),
                        children: [
                          Container(
                            padding: EdgeInsets.only(
                                left: 16, right: 16, bottom: 16),
                            alignment: Alignment.centerLeft,
                            child: Text(question.answer),
                          ),
                        ],
                      ),
                    )
                    .toList(),
              ),
            );
        }
        return LoadingError(
          onRefreshPressed: () => _future = client.getTopicFaq(
            FaqTopic.CEI_PENDENCY,
          ),
        );
      },
    );
  }
}
